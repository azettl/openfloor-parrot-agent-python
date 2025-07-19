from server import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🦜 Parrot Agent server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)