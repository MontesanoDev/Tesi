// V14 verification policy, preregistered before any inference; application unchanged.
// decideC2 is the unchanged V13 cohort-2 policy. V14 rules only add authorization slots,
// the CCIAA branch-only confirmation and natural phrasings, chosen per preregistered variant.
const signer='Leonardo Montemurro',company='Mapi Ingegneria S.r.l.';
const norm=x=>String(x||'').normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase();
const defer='Rinvia questo punto e lascialo vuoto. Non confermo questo punto.';
const forbidden=/attesta|consens|autorizz|accettare|coerent|merceologic|fatturato|miglior triennio|requisit|cause di esclusione|regolarit|casellario|avvalimento|allegat|curricul|eseguir|esecutor|designat|integrazion|assenza di|non sussist|polizza|certificat|copertura|idoneit|incompatibil|servizi svolti|coordinatore|sicurezza/;
const corporate=`Sì, confermo questo ramo: società di ingegneria ${company}, partecipazione in forma singola.`;
const chosen=`Sì, confermo questo ramo: il firmatario scelto per questa domanda è ${signer}, legale rappresentante di ${company}.`;

function decideC2(q,catalogue){
 const form=norm(q.condition||q.context),label=norm(q.label);
 if(q.kind==='decision'||q.kind==='consent')return{text:defer,rule:'defer_procedural'};
 if(forbidden.test(form))return{text:defer,rule:'defer_unconfirmed_attestation_or_designation'};
 if(q.kind==='choice'){
  const options=q.alternatives||[];
  if(/insieme ad altri|contemporaneamente in forme diverse/.test(form)){
   const no=options.filter(x=>/^no(?:\b|$)/.test(norm(x)));
   if(no.length===1)return{text:'Scelgo NO. La partecipazione è in forma singola.',rule:'scenario_no_other_participation'};
   return{text:defer,rule:'unproven_boolean_option_mapping'};
  }
  const engineering=options.filter(x=>/societa di ingegneria/.test(norm(x)));
  if(engineering.length===1&&/partecip|tipologia|nome e per conto|forma|societa/.test(label+' '+form))
   return{text:'Scelgo la voce Società di Ingegneria. La domanda è presentata in forma singola.',rule:'scenario_engineering_option'};
  return{text:defer,rule:'other_choice_not_preregistered'};
 }
 if(q.kind==='applicability'){
  if(/societa(?:[^!?]{0,160})ingegneria/.test(form)||
     /operatore economico|in forma singola|partecipazione singola/.test(form)||
     /^dell[’']impresa\s*$/.test(form)||
     /(?:chiede |di )partecipare (?:alla|a questa)/.test(form))
   return{text:corporate,rule:'scenario_company_and_single_participation'};
  if(/il sottoscritt|la sottoscritt|il\/la sottoscritt|firmatari|sottoscrittore|in qualita di|legale rappresentante|rappresentante legale/.test(form))
   return{text:chosen,rule:'scenario_signer_representation'};
  if(/^\(?eliminare le opzioni non pertinenti\)?$/.test(form))
   return{text:`Per questa domanda scelgo la partecipazione in forma singola come società di ingegneria ${company}; il firmatario scelto è ${signer}.`,rule:'scenario_explicit_choices_only_for_generic_option_instruction'};
  return{text:defer,rule:'unknown_condition_deferred'};
 }
 if(q.kind==='value'&&q.field_ids?.length===1){
  const candidate=catalogue?.candidates?.[q.field_ids[0]];
  const prefix=norm(candidate?.slot_context?.before).trim().replace(/[ :]+$/,'');
  if(/^(?:il(?:\/la)?|la)?\s*(?:sottoscritt[oa](?:\/[oa])?|sottoscrittore|firmatari[oa])$/.test(prefix))
   return{text:`Il firmatario scelto per questa domanda è ${signer}.`,rule:'name_choice_in_verified_name_slot'};
 }
 return{text:defer,rule:'no_factual_values_from_USER'};
}

const VARIANTS={
 'craa-ramo':{cciaaBranch:true,authorizeCciaa:false},
 'craa-autorizza':{cciaaBranch:true,authorizeCciaa:true},
 'cesano-breve':{participation:'Sì, autorizzo.'},
 'cesano-esteso':{participation:`Sì, autorizzo la dichiarazione: la domanda è presentata per conto della Società di Ingegneria ${company}.`},
 'minervino-controllo':{}};
const BRANCH_ONLY=`Sì, ${company} è una società.`;
const DEFER_CCIAA='Rinvio questa dichiarazione: non dichiaro ancora l’attività coerente con la classe merceologica, quindi lascia vuoti quei dati.';
const AUTH_CCIAA='Sì, autorizzo questa dichiarazione con i dati indicati.';
const DEFER_AUTH='Rinvio questa dichiarazione: per ora non la autorizzo.';

function decide(q,catalogue,variant){
 const v=VARIANTS[variant];
 if(!v)throw Error('Unknown preregistered variant '+variant);
 const form=norm(q.condition||q.context);
 const cciaa=/cciaa|camera di commercio/.test(form);
 if(String(q.key||'').startsWith('authorization:')){
  if(cciaa&&v.authorizeCciaa)return{text:AUTH_CCIAA,rule:'v14_full_authorization_cciaa'};
  if(cciaa&&v.cciaaBranch)return{text:DEFER_CCIAA,rule:'v14_defer_cciaa_attestation'};
  if(v.participation&&/societa di ingegneria/.test(form))return{text:v.participation,rule:'v14_authorize_participation_option'};
  return{text:DEFER_AUTH,rule:'v14_defer_other_authorization'};
 }
 if(q.kind==='applicability'&&cciaa&&v.cciaaBranch)return{text:BRANCH_ONLY,rule:'v14_branch_only_confirmation'};
 return decideC2(q,catalogue);
}
function reply(session,catalogue,variant){
 const decisions=(session.chat?.question?.slots||[]).map(q=>({slot:q.slot,key:q.key,kind:q.kind,
   FORM:q.condition||q.context,...decide(q,catalogue,variant)}));
 return{decisions,message:decisions.map(d=>`${d.slot}. ${d.text}`).join('\n')};
}
module.exports={decide,reply,VARIANTS};
