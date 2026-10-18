import Lean

open Lean Elab Meta

def field (j : Json) (key : String) (fallback := "") : String :=
  (j.getObjValAs? String key).toOption.getD fallback

def number (j : Json) (key : String) (fallback : Nat) : Nat :=
  (j.getObjValAs? Nat key).toOption.getD fallback

def object (pairs : List (String × Json)) : Json := Json.mkObj pairs

def parseTerm (text : String) : Term.TermElabM Syntax := do
  match Parser.runParserCategory (← getEnv) `term text with
  | .ok stx => return stx
  | .error error => throwError "{error}"

partial def syntaxKinds (stx : Syntax) : Array String :=
  match stx with
  | .node _ kind children => #[kind.toString] ++ children.foldl (fun acc child => acc ++ syntaxKinds child) #[]
  | _ => #[]

def validateSyntax (stx : Syntax) (allowed : Array String) : Term.TermElabM Unit := do
  if !allowed.isEmpty then
    for kind in syntaxKinds stx do
      if !allowed.contains kind then throwError "unsupported syntax: {kind}"

def addSupport (request : Json) (allowed : Array String) : Term.TermElabM Unit := do
  let supports := (request.getObjValAs? (Array Json) "context").toOption.getD #[]
  if supports.size > 64 then throwError "support declaration limit exceeded"
  for support in supports do
    withTheReader Core.Context (fun ctx => { ctx with currNamespace := (field support "namespace").toName }) do
      let typeSyntax ← parseTerm (field support "type")
      let valueSyntax ← parseTerm (field support "value")
      validateSyntax typeSyntax allowed
      validateSyntax valueSyntax allowed
      let type ← Term.elabType typeSyntax
      Term.synthesizeSyntheticMVarsNoPostponing
      let type ← Term.levelMVarToParam (← instantiateMVars type)
      let value ← Term.elabTermEnsuringType valueSyntax (some type)
      Term.synthesizeSyntheticMVarsNoPostponing
      let value ← instantiateMVars value
      if type.hasMVar || value.hasMVar || type.hasFVar || value.hasFVar then
        throwError "unresolved supporting declaration"
      let name := (field support "name").toName
      let levels := (collectLevelParams (collectLevelParams {} type) value).params.toList
      if ← isProp type then
        addDecl (.thmDecl { name, levelParams := levels, type, value })
      else
        addDecl (.defnDecl { name, levelParams := levels, type, value, hints := .regular 0, safety := .safe })
      enableRealizationsForConst name

def checkProof (request : Json) : Term.TermElabM Json := do
  if field request "action" == "syntax" then
    return object [("status", toJson "syntax"), ("kinds", toJson (syntaxKinds (← parseTerm (field request "proof"))))]
  let allowed := (request.getObjValAs? (Array String) "allowed_syntax").toOption.getD #[]
  for scope in (request.getObjValAs? (Array String) "scopes").toOption.getD #[] do
    activateScoped scope.toName
  addSupport request allowed
  let expectedSyntax ← parseTerm (field request "expected")
  if !allowed.isEmpty then
    for kind in syntaxKinds expectedSyntax do
      if !allowed.contains kind then throwError "unsupported target syntax: {kind}"
  let expected ← Term.elabType expectedSyntax
  Term.synthesizeSyntheticMVarsNoPostponing
  let expected ← Term.levelMVarToParam (← instantiateMVars expected)
  if expected.hasMVar || expected.hasFVar then throwError "unresolved expected type"
  unless ← isProp expected do throwError "expected type must be a proposition"
  let rendering ← ppExpr expected
  if field request "action" == "render" then
    return object [("status", toJson "rendered"), ("type", toJson rendering.pretty)]
  let proofSyntax ← parseTerm (field request "proof")
  if !allowed.isEmpty then
    for kind in syntaxKinds proofSyntax do
      if !allowed.contains kind then throwError "unsupported proof syntax: {kind}"
  let proof ← Term.elabTermEnsuringType proofSyntax (some expected)
  Term.synthesizeSyntheticMVarsNoPostponing
  let proof ← instantiateMVars proof
  if proof.hasMVar || proof.hasFVar then throwError "unresolved proof"
  let actual ← inferType proof
  unless ← isDefEq actual expected do throwError "actual type differs from expected type"
  let levels := (collectLevelParams {} expected).params.toList
  let name := `YamalemmaChecked
  addDecl (.thmDecl { name, levelParams := levels, type := expected, value := proof })
  let axioms ← collectAxioms name
  return object [
    ("status", toJson "checked"),
    ("type", toJson rendering.pretty),
    ("actual_type", toJson (← ppExpr actual).pretty),
    ("axioms", toJson (axioms.map Name.toString)),
    ("type_matches", toJson true)]

partial def syntaxJson (input : String) (stx : Syntax) : Json :=
  object [
    ("kind", toJson stx.getKind.toString),
    ("identifier", toJson (if stx.isIdent then some stx.getId.toString else none)),
    ("start", toJson (stx.getPos?.map (·.byteIdx))),
    ("end", toJson (stx.getTailPos?.map (·.byteIdx))),
    ("text", toJson ((stx.getSubstring?.map (·.toString)).getD "")),
    ("children", toJson (stx.getArgs.map (syntaxJson input)))]

def extractSource (env : Environment) (source : String) : IO Json := do
  let input := Parser.mkInputContext source "source.lean" false
  let (header, initial, messages) ← Parser.parseHeader input
  let mut state := initial
  let mut messages := messages
  let mut commands : Array Json := #[]
  let mut commandState := Command.mkState env
  repeat
    let scope := commandState.scopes.head!
    let pmctx : Parser.ParserModuleContext := { env := commandState.env, options := scope.opts, currNamespace := scope.currNamespace, openDecls := scope.openDecls }
    let (stx, next, newMessages) := Parser.parseCommand input pmctx state messages
    state := next
    messages := newMessages
    if Parser.isTerminalCommand stx then break
    commands := commands.push (syntaxJson source stx)
    if [``Parser.Command.open, ``Parser.Command.namespace, ``Parser.Command.end, ``Parser.Command.section].contains stx.getKind then
      let ctx : Command.Context := { fileName := "source.lean", fileMap := input.fileMap, snap? := none, cancelTk? := none }
      match ← ((Command.elabCommand stx ctx).run commandState).toIO' with
      | .ok (_, newState) => commandState := newState
      | .error error => throw <| IO.userError (← error.toMessageData.toString)
  if messages.hasErrors then
    let errors ← messages.toList.mapM fun m => m.toString
    throw <| IO.userError (String.intercalate "\n" errors)
  return object [("status", toJson "parsed"), ("header", syntaxJson source header), ("commands", toJson commands)]

def runRequest (env : Environment) (request : Json) : IO Json := do
  if field request "action" == "extract" then return ← extractSource env (field request "source")
  let opts := ({} : Options).set `maxHeartbeats (number request "heartbeats" 400000)
    |>.set `pp.parens true |>.set `pp.coercions true
  let action := (checkProof request).run'.run'
  let (result, state) ← action.toIO { fileName := "probe.lean", fileMap := FileMap.ofString "", options := opts, currNamespace := (field request "namespace").toName } { env }
  if state.messages.hasErrors then
    let errors ← state.messages.toList.mapM fun m => m.toString
    throw <| IO.userError (String.intercalate "\n" errors)
  return result

unsafe def main : IO Unit := do
  initSearchPath (← findSysroot)
  enableInitializersExecution
  let env ← importModules #[{ module := `Mathlib }] {} 0 (loadExts := true)
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  stdout.putStrLn (object [("ready", toJson true), ("protocol", toJson (1 : Nat))]).compress
  stdout.flush
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let response ← try
      let request ← IO.ofExcept (Json.parse line)
      let result ← runRequest env request
      pure <| object [("id", toJson (field request "id")), ("result", result)]
    catch error => pure <| object [("error", toJson error.toString)]
    stdout.putStrLn response.compress
    stdout.flush
