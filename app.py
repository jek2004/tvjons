import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-insecure-secret')

def safe_json_loads(env_var, default):
    try:
        val = os.environ.get(env_var, '')
        return json.loads(val) if val.strip() else default
    except Exception as e:
        print(f"⚠️ 环境变量 {env_var} 解析失败: {e}")
        return default

DATA = {
    'vod': safe_json_loads('INIT_VOD_JSON', {"sites": [], "lives": [], "parses": [], "doh": []}),
    'live': safe_json_loads('INIT_LIVE_JSON', [])
}

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect('/admin')
        return '❌ 密码错误！<br><a href="/login">返回登录</a>', 403
    return '''
    <html>
    <head><title>登录</title></head>
    <body style="font-family:sans-serif;text-align:center;padding:50px;">
        <h2>🔒 影视仓源管理登录</h2>
        <form method="post">
            <input type="password" name="password" placeholder="请输入密码" required style="padding:8px;margin:10px;">
            <br>
            <button type="submit" style="padding:8px 20px;">登录</button>
        </form>
    </body>
    </html>
    '''

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('admin.html',
                           vod_json=json.dumps(DATA['vod'], indent=2, ensure_ascii=False),
                           live_json=json.dumps(DATA['live'], indent=2, ensure_ascii=False))

@app.route('/save', methods=['POST'])
def save():
    if not session.get('logged_in'):
        return '未授权', 403
    try:
        DATA['vod'] = json.loads(request.form['vod_json'])
        DATA['live'] = json.loads(request.form['live_json'])
        return '''
        ✅ 保存成功！<br><br>
        <a href="/admin" style="margin:10px;">返回编辑</a>
        <a href="/vod.json" target="_blank" style="margin:10px;">预览 vod.json</a>
        '''
    except Exception as e:
        return f'❌ 错误: {str(e)}<br><a href="/admin">返回</a>'

@app.route('/vod.json')
def vod_json():
    return jsonify(DATA['vod'])

@app.route('/live.json')
def live_json():
    return jsonify(DATA['live'])

@app.route('/')
def index():
    return '''
    <h2>🎬 影视仓源服务</h2>
    <p>✅ 后台运行中</p>
    <p>接口地址：<a href="/vod.json">/vod.json</a></p>
    <p>管理入口：<a href="/login">点击登录</a></p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
