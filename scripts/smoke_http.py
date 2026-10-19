"""Exercise every original route against a disposable local HTTP server."""
import argparse,json,urllib.request,urllib.error,os
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('project',type=int,choices=(1,2,3));parser.add_argument('base_url');parser.add_argument('--output',required=True);parser.add_argument('--refactored',action='store_true');parser.add_argument('--flask-root');args=parser.parse_args()
client=None
if args.flask_root:
 import sys
 os.chdir(args.flask_root);sys.path.insert(0,args.flask_root)
 from app import app
 client=app.test_client()
results=[]
def call(method,path,expected,body=None,headers=None):
 headers={'Content-Type':'application/json',**(headers or {})}
 if args.refactored and path.startswith('/admin/'):
  headers['Authorization']='Bearer '+os.environ['TEST_ADMIN_TOKEN']
 request=urllib.request.Request(args.base_url+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers=headers)
 if client:
  response=client.open(path,method=method,json=body,headers=headers)
  status=response.status_code;raw=response.get_data(as_text=True)
 else:
  return call_network(request,method,path,expected)
 return record_response(method,path,expected,status,raw)
def call_network(request,method,path,expected):
 try:
  with urllib.request.urlopen(request,timeout=8) as response:status=response.status;raw=response.read().decode()
 except urllib.error.HTTPError as ex:status=ex.code;raw=ex.read().decode()
 return record_response(method,path,expected,status,raw)
def record_response(method,path,expected,status,raw):
 try:value=json.loads(raw)
 except json.JSONDecodeError:value=raw
 results.append({'method':method,'path':path,'status':status,'expected':expected,'shape':list(value) if isinstance(value,dict) else ('array' if isinstance(value,list) else 'text'),'passed':status==expected})
 assert status==expected,(method,path,status,raw[:200])
 if args.refactored and isinstance(value,(dict,list)):
  def inspect(x):
   if isinstance(x,dict):
    assert not set(x)&{'password','passwordHash','senha','secret_key'},'Secret field leaked'
    for child in x.values():inspect(child)
   elif isinstance(x,list):
    for child in x:inspect(child)
  inspect(value)
 return value
try:
 if args.project==1:
  call('GET','/',200);call('GET','/health',200)
  call('GET','/produtos',200);call('GET','/produtos/busca?q=Notebook&preco_min=1&preco_max=99999',200)
  product=call('POST','/produtos',201,{'nome':'Produto Teste','descricao':'Contrato','preco':25.5,'estoque':10,'categoria':'geral'})['dados']['id']
  call('GET',f'/produtos/{product}',200)
  call('PUT',f'/produtos/{product}',200,{'nome':'Produto Atualizado','descricao':'Contrato','preco':30,'estoque':10,'categoria':'geral'})
  user=call('POST','/usuarios',201,{'nome':'Pessoa Teste','email':'contrato@example.test','senha':'SenhaTeste123'})['dados']['id']
  call('GET','/usuarios',200);call('GET',f'/usuarios/{user}',200)
  call('POST','/login',200,{'email':'contrato@example.test','senha':'SenhaTeste123'})
  order=call('POST','/pedidos',201,{'usuario_id':user,'itens':[{'produto_id':product,'quantidade':2}]})['dados']['pedido_id']
  call('GET','/pedidos',200);call('GET',f'/pedidos/usuario/{user}',200)
  call('PUT',f'/pedidos/{order}/status',200,{'status':'aprovado'})
  call('GET','/relatorios/vendas',200)
  unused=call('POST','/produtos',201,{'nome':'Excluir Teste','descricao':'','preco':2,'estoque':2,'categoria':'geral'})['dados']['id']
  call('DELETE',f'/produtos/{unused}',200)
  call('POST','/admin/query',200,{'sql':'SELECT COUNT(*) AS count FROM produtos'})
  call('POST','/admin/reset-db',200,{})
 elif args.project==2:
  call('POST','/api/checkout',200,{'usr':'Pessoa Teste','eml':'contrato@example.test','pwd':'SenhaTeste123','c_id':2,'card':'4111222233334444'})
  call('GET','/api/admin/financial-report',200)
  call('DELETE','/api/users/1',200)
 else:
  call('GET','/',200);call('GET','/health',200)
  category=call('POST','/categories',201,{'name':'Categoria Contrato','description':'Teste','color':'#123456'})['id']
  call('GET','/categories',200)
  user=call('POST','/users',201,{'name':'Pessoa Teste','email':'contrato@example.test','password':'SenhaTeste123','role':'user'})['id']
  call('GET','/users',200);call('GET',f'/users/{user}',200)
  call('POST','/login',200,{'email':'contrato@example.test','password':'SenhaTeste123'})
  task=call('POST','/tasks',201,{'title':'Contrato de tarefa','description':'Teste','priority':2,'user_id':user,'category_id':category,'tags':['teste'],'due_date':'2030-01-01'})['id']
  call('GET','/tasks',200);call('GET',f'/tasks/{task}',200);call('GET','/tasks/search?q=Contrato&priority=2',200);call('GET','/tasks/stats',200)
  call('PUT',f'/tasks/{task}',200,{'title':'Contrato atualizado','status':'done','priority':3})
  call('GET',f'/users/{user}/tasks',200);call('GET','/reports/summary',200);call('GET',f'/reports/user/{user}',200)
  call('PUT',f'/users/{user}',200,{'name':'Pessoa Atualizada'})
  call('PUT',f'/categories/{category}',200,{'name':'Categoria Atualizada'})
  call('DELETE',f'/tasks/{task}',200);call('DELETE',f'/categories/{category}',200);call('DELETE',f'/users/{user}',200)
finally:
 Path(args.output).write_text(json.dumps({'project':args.project,'refactored':args.refactored,'requests':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results)},indent=2)+'\n')
 print(json.dumps({'project':args.project,'requests':len(results),'passed':sum(x['passed'] for x in results)}))
