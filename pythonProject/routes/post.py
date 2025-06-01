from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.post import Post

post_bp = Blueprint('post_bp', __name__, url_prefix='/posts')


@post_bp.route('', methods=['GET'])
@jwt_required()
def get_posts():
    user_id = int(get_jwt_identity())
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()

    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at.isoformat()
    } for post in posts])


@post_bp.route('', methods=['POST'])
@jwt_required()
def create_post():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    post = Post(user_id=user_id, title=title, content=content)
    db.session.add(post)
    db.session.commit()

    return jsonify({'message': 'Post created'}), 201


@post_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.filter_by(id=post_id, user_id=user_id).first()

    if not post:
        return jsonify({'error': 'Post not found or unauthorized'}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'})
