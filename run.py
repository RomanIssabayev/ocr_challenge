from app import create_app, create_first_user, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all(bind_key="users")
        create_first_user()
    app.run(debug=True)