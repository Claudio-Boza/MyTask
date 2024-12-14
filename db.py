from sqlalchemy import create_engine, Column, String, Integer, Date, Boolean, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'task'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    finalizada = Column(Boolean, default=False)

    @property
    def json(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'data': self.data,
            'finalizada': self.finalizada
        }
        
engine = create_engine('sqlite:///task.db')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def add_task(task: Task):
    try:
        session.add(task)
        session.commit()
        return task
    except Exception as e:        
        session.rollback()
        return False

def delete_task(task_id):
    try:
        busca_task = session.query(Task).where(Task.id == task_id).first()        
        if busca_task != None:
            session.delete(busca_task)
        else:
            return False
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False

def get_task_all() -> list:
    try:
        lista = []
        busca = session.query(Task).order_by(Task.finalizada.asc()).all()
        for task in busca:
            lista.append(task)
        return lista
    except Exception as e:
        session.rollback()
        return False

def get_task(task: Task):
    try:        
        busca = session.query(Task).where(Task.id == task.id).first()
        return busca.json
    except Exception as e:
        session.rollback()
        return False

def get_task_not_finalize():
    try:
        lista = []
        busca = session.query(Task).where(Task.finalizada == False).all()
        for i in busca:
            lista.append(i)
        return lista
    except Exception as e:
        return False
    
def delete_task_all():
    try:
        lista = get_task_all()
        for i in lista:
            session.delete(i)
        session.commit()
    except Exception as e:
        session.rollback()
        return False
    
def atualiza_task(task: Task):
    try:
        session.query(Task).filter_by(id= task.id).update({
            Task.descricao: f'{task.descricao}',
            Task.data: task.data,
            Task.finalizada: task.finalizada
        })
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False

def finaliza_task(task: Task):
    try:
        session.query(Task).filter_by(id= task.id).update({
            Task.finalizada: not task.finalizada
        })
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False

if __name__ == '__main__':
    # task = Task(
    #     # id= 2,
    #     descricao = 'Teste True',
    #     data = datetime.now(),
    #     finalizada = True
    # )
    # delete_task_all()
    # add_task(task)
    # if delete_task(2):
    #     print('deletado')
    # else:
    #     print('Não deletado')
    # add_task(task)
    # print(get_task(task))
    # finaliza_task(task)
    
    # for i in range(10000):
    #     task = Task(        
    #         descricao = 'Teste Nois',
    #         data = datetime.now(),
    #         finalizada = False
    #     )
    # session.add(task)
    # session.commit()
    # print(get_task_all())
    # delete_task_all()
    # teste = get_task_all()
    # for i in teste:
    #     print(i.json)
    ...