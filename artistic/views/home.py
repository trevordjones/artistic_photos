from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required

home_bp = Blueprint('home', __name__)
@home_bp.route('/', methods=['GET', 'POST'])
@login_required
def main():
    import subprocess

    from artistic.kaggle_script import create_kaggle_script

    if request.method == 'GET':
        return render_template('home/index.html')
    else:
        image_name = binascii.b2a_hex(os.urandom(5)).decode('utf-8')
        names = {'content': '', 'style': ''}
        try:
            for key in request.files:
                image = Image.upload_to_gcp(request.files[key], key, image_name)
                names[key] = image.source_name
                with app.app_context():
                    image.save()
            create_kaggle_script(names['content'], names['style'], 'random')
            subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
            os.remove(ROOT.joinpath('temp/nst.py'), missing_ok=True)
            os.remove(ROOT.joinpath('temp/kernel-metadata.json'), missing_ok=True)
        except Exception as e:
            print(e)

        return redirect(url_for('main'))
