// Preregistered deterministic USER policy for the synthetic branch scenario (25 October 2026).
// Confirms only the scenario branches (RT not yet formed, reliance on Geo Lab S.r.l.), denies the
// single-participation and own-requirements branches, defers everything else. No factual values.
const norm=x=>String(x||'').normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase();
const defer='Rinvia questo punto e lascialo vuoto. Non confermo questo punto.';
const RT='Sì, confermo questo ramo: partecipiamo come raggruppamento temporaneo non ancora costituito, mandataria Mapi Ingegneria S.r.l. e mandante Studio Tecnico Associato Ferri.';
const AUX='Sì, confermo questo ramo: ci avvaliamo dei requisiti dell’impresa ausiliaria Geo Lab S.r.l.';
const NO_SINGLE='No, questo ramo non si applica: non partecipiamo in forma singola.';
const NO_OWN='No, questo ramo non si applica: ci avvaliamo dei requisiti dell’impresa ausiliaria Geo Lab S.r.l.';
function decide(q){
 const form=norm(q.condition||q.context);
 if(q.kind==='decision'||q.kind==='consent')return{text:defer,rule:'defer_procedural'};
 if(String(q.key||'').startsWith('authorization:')){
  if(/raggruppament|mandatari|mandant/.test(form))return{text:'Sì, autorizzo la dichiarazione per il raggruppamento indicato.',rule:'authorize_rt'};
  if(/avval|ausiliari/.test(form))return{text:'Sì, autorizzo la dichiarazione di avvalimento dell’impresa ausiliaria Geo Lab S.r.l.',rule:'authorize_aux'};
  return{text:'Rinvio questa dichiarazione: per ora non la autorizzo.',rule:'defer_authorization'};
 }
 if(q.kind==='applicability'||q.kind==='choice'){
  if(/forma singola|operatore economico singolo/.test(form))return{text:NO_SINGLE,rule:'deny_single'};
  if(/propri requisiti|in proprio/.test(form))return{text:NO_OWN,rule:'deny_own_requirements'};
  if(/raggruppament|mandatari|mandant/.test(form))return{text:RT,rule:'confirm_rt'};
  if(/avval|ausiliari/.test(form))return{text:AUX,rule:'confirm_aux'};
  return{text:defer,rule:'unknown_condition_deferred'};
 }
 return{text:defer,rule:'no_factual_values_from_USER'};
}
function reply(session){
 const decisions=(session.chat?.question?.slots||[]).map(q=>({slot:q.slot,key:q.key,kind:q.kind,
   FORM:q.condition||q.context,...decide(q)}));
 return{decisions,message:decisions.map(d=>`${d.slot}. ${d.text}`).join('\n')};
}
module.exports={decide,reply};
