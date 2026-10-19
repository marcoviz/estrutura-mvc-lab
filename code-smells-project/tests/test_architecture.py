import os,tempfile,sys,unittest,sqlite3
from pathlib import Path
TARGET=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TARGET));temp=tempfile.TemporaryDirectory();os.environ['DATABASE_PATH']=str(Path(temp.name)/'bootstrap.db')
from app import create_app
from database import get_db
class StoreTests(unittest.TestCase):
 def setUp(self):
  self.directory=tempfile.TemporaryDirectory();self.app=create_app({'DATABASE':str(Path(self.directory.name)/'test.db'),'TESTING':True,'ADMIN_TOKEN':'temporary-test-admin'});self.client=self.app.test_client()
 def tearDown(self):self.directory.cleanup()
 def user(self):return self.client.post('/usuarios',json={'nome':'Teste','email':'test@example.test','senha':'correct-password'}).json['dados']['id']
 def product(self):return self.client.post('/produtos',json={'nome':'Livro Teste','preco':20,'estoque':5,'categoria':'livros'}).json['dados']['id']
 def test_user_password_and_sql_literals(self):
  uid=self.user();data=self.client.get(f'/usuarios/{uid}').json['dados'];self.assertNotIn('senha',data)
  self.assertEqual(self.client.post('/login',json={'email':'test@example.test','senha':'correct-password'}).status_code,200)
  self.assertEqual(self.client.post('/login',json={'email':"' OR 1=1 --",'senha':'wrong'}).status_code,401)
  response=self.client.post('/produtos',json={'nome':"Livro d'arte",'preco':2,'estoque':3,'categoria':'livros'});self.assertEqual(response.status_code,201)
  self.assertNotIn('secret_key',self.client.get('/health').json)
 def test_password_preserves_whitespace_and_rejects_non_text(self):
  response=self.client.post('/usuarios',json={'nome':'Espaçado','email':'spaces@example.test','senha':' pass '})
  self.assertEqual(response.status_code,201)
  self.assertEqual(self.client.post('/login',json={'email':'spaces@example.test','senha':' pass '}).status_code,200)
  self.assertEqual(self.client.post('/login',json={'email':'spaces@example.test','senha':'pass'}).status_code,401)
  self.assertEqual(self.client.post('/login',json={'email':'spaces@example.test','senha':[]}).status_code,400)
 def test_order_rollback_and_aggregate_stock(self):
  uid=self.user();pid=self.product()
  with self.app.app_context():
   db=get_db();db.execute("CREATE TRIGGER fail_item BEFORE INSERT ON itens_pedido BEGIN SELECT RAISE(ABORT, 'test'); END");db.commit()
  response=self.client.post('/pedidos',json={'usuario_id':uid,'itens':[{'produto_id':pid,'quantidade':1}]});self.assertEqual(response.status_code,500)
  with self.app.app_context():
   db=get_db();self.assertEqual(db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0],0);self.assertEqual(db.execute('SELECT estoque FROM produtos WHERE id=?',(pid,)).fetchone()[0],5);db.execute('DROP TRIGGER fail_item');db.commit()
  response=self.client.post('/pedidos',json={'usuario_id':uid,'itens':[{'produto_id':pid,'quantidade':3},{'produto_id':pid,'quantidade':3}]});self.assertEqual(response.status_code,400)
  response=self.client.post('/pedidos',json={'usuario_id':uid,'itens':[{'produto_id':pid,'quantidade':2},{'produto_id':pid,'quantidade':1}]});self.assertEqual(response.status_code,201);self.assertEqual(response.json['dados']['total'],60)
 def test_validation_and_admin_boundary(self):
  self.assertEqual(self.client.get('/produtos/busca?preco_min=abc').status_code,400)
  self.assertEqual(self.client.post('/produtos',json={'nome':'Livro','preco':'bad','estoque':2}).status_code,400)
  self.assertEqual(self.client.post('/admin/reset-db',json={}).status_code,401)
  headers={'Authorization':'Bearer temporary-test-admin'}
  self.assertEqual(self.client.post('/admin/query',json={'sql':'DELETE FROM usuarios'},headers=headers).status_code,400)
  self.assertEqual(self.client.post('/admin/query',json={'sql':'SELECT COUNT(*) AS count FROM produtos'},headers=headers).status_code,200)
  for category in ([], {}):
   self.assertEqual(self.client.post('/produtos',json={'nome':'Produto','preco':1,'estoque':1,'categoria':category}).status_code,400)
  for status in ([], {}):
   self.assertEqual(self.client.put('/pedidos/1/status',json={'status':status}).status_code,400)
 def test_order_list_uses_two_queries(self):
  uid=self.user();pid=self.product()
  for _ in range(3):self.client.post('/pedidos',json={'usuario_id':uid,'itens':[{'produto_id':pid,'quantidade':1}]})
  from models.orders import Orders
  with self.app.app_context():
   db=get_db();queries=[];db.set_trace_callback(queries.append);result=Orders(db).list();self.assertEqual(len(result),3);self.assertEqual(len(queries),2)
if __name__=='__main__':unittest.main()
