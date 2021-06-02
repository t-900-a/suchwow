from flask import jsonify, Blueprint, url_for, request, abort
from suchwow.models import Post
from suchwow import wownero


bp = Blueprint("api", "api")

@bp.route("/api/list")
def api_list():
    limit = request.args.get('limit', 30)
    offset = request.args.get('offset', 0)

    # Hacky way to convert query str value to int
    try:
        limit = int(limit)
        offset = int(offset)
    except:
        abort(500, "Bleep bleep")

    if limit > 30:
        limit = 30

    all_posts = []
    posts = Post.select().where(Post.approved==True).order_by(Post.timestamp.desc()).limit(limit).offset(offset)
    for post in posts:
        wallet = wownero.Wallet()
        if wallet.connected:
            address = wallet.get_address(account=post.account_index)
        else:
            address = ''

        payload = {
            'image': url_for('post.uploaded_file', filename=post.image_name, _external=True),
            'submitter': post.submitter,
            'address': address,
            'title': post.title,
            'text': post.text,
            'href': url_for('post.read', id=post.id, _external=True),
            'id': post.id,
            'timestamp': post.timestamp
        }
        all_posts.append(payload)
    return jsonify(all_posts)
