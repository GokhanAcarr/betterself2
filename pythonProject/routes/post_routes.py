from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Post, User
from flasgger.utils import swag_from

post_bp = Blueprint('post_bp', __name__, url_prefix='/posts')


@post_bp.route('', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Post'],
    'description': 'Get all user posts',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'List of posts',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'content': {'type': 'string'},
                        'created_at': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_posts():
    posts = Post.query.all()
    return jsonify([{
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at.isoformat()
    } for post in posts])


@post_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Post'],
    'description': 'Create a new post',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['title', 'content'],
            'properties': {
                'title': {'type': 'string'},
                'content': {'type': 'string'}
            }
        }
    }],
    'responses': {
        201: {'description': 'Post created'},
        400: {'description': 'Missing title or content'}
    }
})
def create_post():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Title and content are required."}), 400

    post = Post(user_id=user_id, title=title, content=content)
    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created"}), 201


@post_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Post'],
    'description': 'Delete a post (admin only)',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'post_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID of the post to delete'
    }],
    'responses': {
        200: {'description': 'Post deleted'},
        403: {'description': 'Unauthorized'},
        404: {'description': 'Post not found'}
    }
})
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted successfully"})
