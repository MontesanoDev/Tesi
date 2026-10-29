// Preregistered USER policy, matching revision 2 (28 Oct 2026, after attempt 03).
// Each shown slot gets one scenario rule from its real kind, FORM quote and destinations;
// the answer texts stay in the private scenario file that calls policy(ANSWERS).
// Revision 1 read every slot kind as condition/choice/value and matched dates on any
// destination list: attempt 03 answered the company branch with the dates text and
// deferred the operator confirmation (both recorded as SKIP, not changed here).
const norm=s=>String(s||'').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu,'')
  .replace(/[’`]/g,"'").replace(/\s+/g,' ').trim();
const CONFIRMABLE=new Set(['applicability','condition','choice']);
const DEFERRED=/dichiarazion|attestazion|requisit|designazion|designi|categor|fasc[ei]|luogo e data/;

function rule(slot){
  const ids=slot.field_ids||[];
  const form=norm([slot.condition,slot.context].filter(Boolean).join(' '));  // FORM quote
  const ask=norm([slot.question,slot.label].filter(Boolean).join(' '));
  if(slot.kind==='authorization'||slot.authorization||slot.kind==='decision')return 'defer';
  if(CONFIRMABLE.has(slot.kind)){
    if(/legale rappresentante di societa di professionisti/.test(form)
       &&/societa di ingegneria/.test(form))return 'corporate';
    // The signatory block: with the role among the destinations, the role confirmation
    // (it names the person and the documented office); the name alone otherwise.
    if(/^\W*il sottoscritto\b/.test(form)&&ids.some(id=>/^p1[234]\./.test(id)))
      return ids.includes('p14.s0')?'role':'name';
    if(/(?:^|\W)dell'operatore economico\W*$/.test(form)&&ids.includes('p14.s1'))return 'company';
    if(/partecip/.test(ask+' '+form)&&/singol|raggrupp/.test(ask+' '+form))return 'single';
    return 'defer';
  }
  if(slot.kind==='value'&&ids.length===1){
    if(DEFERRED.test(ask))return 'defer';
    if(/^dal\b|data.*iscrizion|iscrizion.*data/.test(norm(slot.label))
       ||/data.*iscrizion|iscrizion.*data/.test(ask))return 'dates';
    if(ids[0]==='p12.s0')return 'name';
    if(ids[0]==='p14.s0')return 'role';
    if(ids[0]==='p14.s1')return 'company';
  }
  return 'defer';
}

function policy(ANSWERS){
  function reply(session){
    const slots=session?.chat?.question?.slots||[];
    const rows=slots.map(s=>{
      const r=rule(s);
      return {slot:s.slot,key:s.key,field_ids:s.field_ids||[],kind:s.kind,question:s.question,
              context:s.context,rule:r,answer:ANSWERS[r]};
    });
    return {rows,message:rows.map(r=>`${r.slot}. ${r.answer}`).join('\n')};
  }
  return {reply,rule,ANSWERS,revision:2};
}
module.exports={policy,rule};
