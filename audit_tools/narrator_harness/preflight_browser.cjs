// Real React composer and FastAPI. No API routes are mocked or fulfilled.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.AUDIT_PLAYWRIGHT);
const [root,base,scenario]=process.argv.slice(2);
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--disable-background-networking']});
 const context=await browser.newContext();
 const denied=[],network=[];
 await context.route('**/*',route=>{
  const host=new URL(route.request().url()).hostname;
  if(!['127.0.0.1','localhost','::1'].includes(host)){denied.push(route.request().url());return route.abort();}
  return route.continue();
 });
 const page=await context.newPage();page.setDefaultTimeout(30000);
 page.on('response',r=>{if(r.url().includes('/api/'))network.push({url:r.url(),status:r.status()});});
 const result={scenario,simulated:true,frontend_real:true,api_mocked:false,started:new Date().toISOString()};
 try{
  await page.goto(base+'/projects/preflight');
  const composer=page.getByRole('textbox',{name:'Messaggio per l’assistente'});
  await composer.fill('Ciao, questa è una verifica sintetica del trasporto.');
  const responsePromise=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/answer'));
  await page.getByRole('button',{name:'Invia',exact:true}).click();
  const response=await responsePromise;await response.finished();
  result.status=response.status();try{result.response=await response.json();}catch{result.response={raw:await response.text()};}
  result.browser_timing=response.request().timing();
  result.dom=await page.locator('body').innerText();
  if(scenario==='success'){
   result.probes={};
   for(const name of ['async_denied','async_allowed','sync_denied','sync_allowed','external_allowed','network_denial']){
    result.probes[name]=await page.evaluate(async name=>{
      const r=await fetch('/api/__audit-probe/'+name,{method:'POST'});return {status:r.status,body:await r.json()};
    },name);
   }
  }
 }catch(e){result.error=e.stack;process.exitCode=1;}
 finally{
  result.finished=new Date().toISOString();result.network=network;result.external_requests_denied=denied;
  fs.writeFileSync(path.join(root,'browser-result.json'),JSON.stringify(result,null,2));
  await context.close();await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1;});
