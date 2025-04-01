from time import sleep
import pytest
import os
from datetime import datetime, timedelta
import grpc
from concurrent import futures

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from proto import post_pb2
from proto import post_pb2_grpc
from app import PostService, Base, engine
import datetime as dt

def parse_grpc_timestamp(timestamp_str):
    if timestamp_str.endswith('Z'):
        d = datetime.fromisoformat(timestamp_str[:-1] + '+00:00')
    else:
        d = datetime.fromisoformat(timestamp_str + '+00:00')
    return d.replace(tzinfo=None)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def post_service():
    return PostService()

@pytest.fixture
def grpc_server(post_service):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostServiceServicer_to_server(post_service, server)
    server.add_insecure_port('[::]:50052')
    server.start()
    yield server
    server.stop(0)

def test_create_post(post_service):
    request = post_pb2.CreatePostRequest(
        post_data=post_pb2.PostData(
            title="Test Post",
            description="Test Description",
            is_private=False,
            tags=["test", "grpc"]
        ),
        creator_id=1
    )
    
    response = post_service.CreatePost(request, None)
    
    assert response.post.id == 1
    assert response.post.data.title == "Test Post"
    assert response.post.creator_id == 1
    assert not response.post.data.is_private
    assert "test" in response.post.data.tags

def test_get_post(post_service):
    create_resp = post_service.CreatePost(
        post_pb2.CreatePostRequest(
            post_data=post_pb2.PostData(
                title="Existing Post",
                description="Existing Description",
                is_private=True,
                tags=["existing"]
            ),
            creator_id=1
        ),
        None
    )
    
    request = post_pb2.GetPostRequest(
        post_id=create_resp.post.id,
        creator_id=1
    )
    response = post_service.GetPost(request, None)
    
    assert response.post.id == create_resp.post.id
    assert response.post.data.title == "Existing Post"
    assert response.post.data.is_private
    assert not response.error

def test_get_post_not_found(post_service):
    request = post_pb2.GetPostRequest(post_id=999, creator_id=1)
    response = post_service.GetPost(request, None)
    assert response.error == "Post not found"

def test_get_public_post(post_service):
    create_resp = post_service.CreatePost(
        post_pb2.CreatePostRequest(
            post_data=post_pb2.PostData(
                title="Public Post",
                description="Public",
                is_private=False,
                tags=[]
            ),
            creator_id=2
        ),
        None
    )
    
    request = post_pb2.GetPostRequest(
        post_id=create_resp.post.id,
        creator_id=1
    )
    response = post_service.GetPost(request, None)
    
    assert response.post.id == create_resp.post.id
    assert response.post.data.title == "Public Post"
    assert not response.post.data.is_private
    assert not response.error

def test_get_post_permission_denied(post_service):
    create_resp = post_service.CreatePost(
        post_pb2.CreatePostRequest(
            post_data=post_pb2.PostData(
                title="Private Post",
                description="Only for owner",
                is_private=True,
                tags=[]
            ),
            creator_id=2
        ),
        None
    )
    
    request = post_pb2.GetPostRequest(
        post_id=create_resp.post.id,
        creator_id=1
    )
    response = post_service.GetPost(request, None)
    
    assert response.error == "Permission denied"

def test_update_post_not_found(post_service):
    request = post_pb2.UpdatePostRequest(
        post_id=1000,
        creator_id=1,
        post_data=post_pb2.PostData(
            title="New Title",
            description="New Description",
            is_private=True,
            tags=["new"]
        )
    )
    response = post_service.UpdatePost(request, None)
    assert response.error == "Post not found"

def test_update_post(post_service):
    create_resp = post_service.CreatePost(
        post_pb2.CreatePostRequest(
            post_data=post_pb2.PostData(
                title="Old Title",
                description="Old Description",
                is_private=False,
                tags=["old"]
            ),
            creator_id=1
        ),
        None
    )
    created_at = parse_grpc_timestamp(create_resp.post.created_at)
    initial_updated_at = parse_grpc_timestamp(create_resp.post.updated_at)
    
    assert dt.datetime.utcnow().replace(tzinfo=None) - created_at < timedelta(seconds=1)
    assert dt.datetime.utcnow().replace(tzinfo=None) - initial_updated_at < timedelta(seconds=1)
    
    invalid_request = post_pb2.UpdatePostRequest(
        post_id=create_resp.post.id,
        creator_id=2,
        post_data=post_pb2.PostData(
            title="New Title",
            description="New Description",
            is_private=True,
            tags=["new"]
        )
    )
    invalid_response = post_service.UpdatePost(invalid_request, None)
    assert invalid_response.error == "Permission denied"
    
    request = post_pb2.GetPostRequest(
        post_id=create_resp.post.id,
        creator_id=1
    )
    response = post_service.GetPost(request, None)
    assert response.post.data.title == "Old Title"
    assert response.post.data.description == "Old Description"
    assert not response.post.data.is_private
    assert "old" in response.post.data.tags
    
    sleep(3)
    
    update_request = post_pb2.UpdatePostRequest(
        post_id=create_resp.post.id,
        creator_id=1,
        post_data=post_pb2.PostData(
            title="New Title",
            description="New Description",
            is_private=True,
            tags=["new"]
        )
    )
    
    response = post_service.UpdatePost(update_request, None)
    
    new_created_at = parse_grpc_timestamp(response.post.created_at)
    updated_at = parse_grpc_timestamp(response.post.updated_at)
    
    assert new_created_at == created_at
    assert dt.datetime.utcnow().replace(tzinfo=None) - updated_at < timedelta(seconds=1)
    
    assert response.post.data.title == "New Title"
    assert response.post.data.description == "New Description"
    assert response.post.data.is_private
    assert "new" in response.post.data.tags

def test_delete_post_not_found(post_service):
    request = post_pb2.DeletePostRequest(post_id=999, creator_id=1)
    response = post_service.DeletePost(request, None)
    assert response.error == "Post not found"

def test_delete_post(post_service):
    create_resp = post_service.CreatePost(
        post_pb2.CreatePostRequest(
            post_data=post_pb2.PostData(
                title="To Delete",
                description="Will be deleted",
                is_private=False,
                tags=[]
            ),
            creator_id=1
        ),
        None
    )
    
    invalid_request = post_pb2.DeletePostRequest(
        post_id=create_resp.post.id,
        creator_id=2,
    )
    invalid_response = post_service.DeletePost(invalid_request, None)
    assert invalid_response.error == "Permission denied"
    
    request = post_pb2.GetPostRequest(
        post_id=create_resp.post.id,
        creator_id=1
    )
    response = post_service.GetPost(request, None)
    assert response.post.data.title == "To Delete"
    
    request = post_pb2.DeletePostRequest(
        post_id=create_resp.post.id,
        creator_id=1
    )
    response = post_service.DeletePost(request, None)
    
    get_request = post_pb2.GetPostRequest(
        post_id=create_resp.post.id,
        creator_id=1
    )
    get_response = post_service.GetPost(get_request, None)
    assert get_response.error == "Post not found"

def test_list_posts(post_service):
    for i in range(3):
        post_service.CreatePost(
            post_pb2.CreatePostRequest(
                post_data=post_pb2.PostData(
                    title=f"Post {i}",
                    description=f"Description {i}",
                    is_private=False,
                    tags=[]
                ),
                creator_id=7
            ),
            None
        )
    
    request = post_pb2.ListPostsRequest(creator_id=7)
    response = post_service.ListPosts(request, None)
    
    assert len(response.posts) == 3
    assert all(p.creator_id == 7 for p in response.posts)
    