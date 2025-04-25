from concurrent import futures
import grpc
from datetime import datetime
from sqlalchemy.orm import Session

from proto import post_pb2
from proto import post_pb2_grpc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
import datetime as dt

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    is_private = Column(Boolean)
    tags = Column(JSON)
    creator_id = Column(Integer)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, 
                       onupdate=dt.datetime.utcnow)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PostService(post_pb2_grpc.PostServiceServicer):
    def CreatePost(self, request, context):
        db: Session = next(get_db())
        
        created_at = dt.datetime.utcnow()
        
        post = Post(
            title=request.post_data.title,
            description=request.post_data.description,
            is_private=request.post_data.is_private,
            tags=list(request.post_data.tags),
            creator_id=request.creator_id,
            created_at=created_at,
            updated_at=created_at
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        return post_pb2.PostResponse(post=self._post_to_proto(post))
    
    def GetPost(self, request, context):
        db: Session = next(get_db())
        post = db.query(Post).filter(Post.id == request.post_id).first()
        
        if not post:
            return post_pb2.PostResponse(error="Post not found")
        
        if (post.creator_id != request.creator_id) and post.is_private:
            return post_pb2.PostResponse(error="Permission denied")
            
        return post_pb2.PostResponse(post=self._post_to_proto(post))
    
    def UpdatePost(self, request, context):
        db: Session = next(get_db())
        post = db.query(Post).filter(Post.id == request.post_id).first()
        
        if not post:
            return post_pb2.PostResponse(error="Post not found")
        
        if post.creator_id != request.creator_id:
            return post_pb2.PostResponse(error="Permission denied")
            
        post.title = request.post_data.title
        post.description = request.post_data.description
        post.is_private = request.post_data.is_private
        post.tags = list(request.post_data.tags)
        post.updated_at = dt.datetime.utcnow()
        
        db.commit()
        db.refresh(post)
        
        return post_pb2.PostResponse(post=self._post_to_proto(post))
    
    def DeletePost(self, request, context):
        db: Session = next(get_db())
        post = db.query(Post).filter(Post.id == request.post_id).first()
        
        if not post:
            return post_pb2.DeletePostResponse(error="Post not found")
        
        if post.creator_id != request.creator_id:
            return post_pb2.DeletePostResponse(error="Permission denied")
            
        db.delete(post)
        db.commit()
        
        return post_pb2.DeletePostResponse()
    
    def ListPosts(self, request, context):
        db: Session = next(get_db())
        posts = db.query(Post).filter(Post.creator_id == request.creator_id).all()
        
        return post_pb2.ListPostsResponse(
            posts=[self._post_to_proto(post) for post in posts]
        )
    
    def _post_to_proto(self, post: Post):
        return post_pb2.Post(
            id=post.id,
            data=post_pb2.PostData(
                title=post.title,
                description=post.description,
                is_private=post.is_private,
                tags=post.tags or []
            ),
            creator_id=post.creator_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )

def serve():
    init_db()
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
