# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: proto/post.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'proto/post.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10proto/post.proto\x12\x04post\"P\n\x08PostData\x12\r\n\x05title\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x12\n\nis_private\x18\x07 \x01(\x08\x12\x0c\n\x04tags\x18\x08 \x03(\t\"l\n\x04Post\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x1c\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x0e.post.PostData\x12\x12\n\ncreator_id\x18\x03 \x01(\x05\x12\x12\n\ncreated_at\x18\x04 \x01(\t\x12\x12\n\nupdated_at\x18\x05 \x01(\t\"K\n\x11\x43reatePostRequest\x12!\n\tpost_data\x18\x01 \x01(\x0b\x32\x0e.post.PostData\x12\x13\n\ncreator_id\x18\xe8\x07 \x01(\x05\"9\n\x11\x44\x65letePostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\x05\x12\x13\n\ncreator_id\x18\xe8\x07 \x01(\x05\"\\\n\x11UpdatePostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\x05\x12!\n\tpost_data\x18\x02 \x01(\x0b\x32\x0e.post.PostData\x12\x13\n\ncreator_id\x18\xe8\x07 \x01(\x05\"6\n\x0eGetPostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\x05\x12\x13\n\ncreator_id\x18\xe8\x07 \x01(\x05\"\'\n\x10ListPostsRequest\x12\x13\n\ncreator_id\x18\xe8\x07 \x01(\x05\"8\n\x0cPostResponse\x12\x18\n\x04post\x18\x01 \x01(\x0b\x32\n.post.Post\x12\x0e\n\x05\x65rror\x18\xe8\x07 \x01(\t\"$\n\x12\x44\x65letePostResponse\x12\x0e\n\x05\x65rror\x18\xe8\x07 \x01(\t\">\n\x11ListPostsResponse\x12\x19\n\x05posts\x18\x01 \x03(\x0b\x32\n.post.Post\x12\x0e\n\x05\x65rror\x18\xe8\x07 \x01(\t2\xb7\x02\n\x0bPostService\x12\x39\n\nCreatePost\x12\x17.post.CreatePostRequest\x1a\x12.post.PostResponse\x12?\n\nDeletePost\x12\x17.post.DeletePostRequest\x1a\x18.post.DeletePostResponse\x12\x39\n\nUpdatePost\x12\x17.post.UpdatePostRequest\x1a\x12.post.PostResponse\x12\x33\n\x07GetPost\x12\x14.post.GetPostRequest\x1a\x12.post.PostResponse\x12<\n\tListPosts\x12\x16.post.ListPostsRequest\x1a\x17.post.ListPostsResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.post_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_POSTDATA']._serialized_start=26
  _globals['_POSTDATA']._serialized_end=106
  _globals['_POST']._serialized_start=108
  _globals['_POST']._serialized_end=216
  _globals['_CREATEPOSTREQUEST']._serialized_start=218
  _globals['_CREATEPOSTREQUEST']._serialized_end=293
  _globals['_DELETEPOSTREQUEST']._serialized_start=295
  _globals['_DELETEPOSTREQUEST']._serialized_end=352
  _globals['_UPDATEPOSTREQUEST']._serialized_start=354
  _globals['_UPDATEPOSTREQUEST']._serialized_end=446
  _globals['_GETPOSTREQUEST']._serialized_start=448
  _globals['_GETPOSTREQUEST']._serialized_end=502
  _globals['_LISTPOSTSREQUEST']._serialized_start=504
  _globals['_LISTPOSTSREQUEST']._serialized_end=543
  _globals['_POSTRESPONSE']._serialized_start=545
  _globals['_POSTRESPONSE']._serialized_end=601
  _globals['_DELETEPOSTRESPONSE']._serialized_start=603
  _globals['_DELETEPOSTRESPONSE']._serialized_end=639
  _globals['_LISTPOSTSRESPONSE']._serialized_start=641
  _globals['_LISTPOSTSRESPONSE']._serialized_end=703
  _globals['_POSTSERVICE']._serialized_start=706
  _globals['_POSTSERVICE']._serialized_end=1017
# @@protoc_insertion_point(module_scope)
