import bcrypt

from .db_query import Database

db = Database()

class PgPersistence:

    def __init__(self):
        pass

    def is_unique_constraint_violation(self, error):
        return "violates unique constraint" in str(error)

    async def create_user(self, username, password):

        check_user = """
            SELECT id
            FROM users
            WHERE username = $1
        """

        existing_user = await db.db_query(
            check_user,
            username
        )

        if len(existing_user) > 0:
            return False

        # bcrypt is synchronous in Python
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(10)
        ).decode("utf-8")

        create_user_query = """
            INSERT INTO users(username, password)
            VALUES($1, $2)
            RETURNING id, username
        """

        try:
            result = await db.db_query(
                create_user_query,
                username,
                hashed_password
            )

            return dict(result[0])

        except Exception as error:

            if self.is_unique_constraint_violation(error):
                return False

            raise

    async def authenticate(self, username, password):

        find_user = """
            SELECT id, username, password
            FROM users
            WHERE username = $1
        """

        result = await db.db_query(
            find_user,
            username
        )

        if len(result) == 0:
            return False

        user = result[0]

        password_match = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

        if not password_match:
            return False

        return {
            "id": user["id"],
            "username": user["username"]
        }

    async def get_user_by_id(self, id):

        query = """
            SELECT id, username
            FROM users
            WHERE id = $1
        """

        result = await db.db_query(
            query,
            id
        )

        if len(result) == 0:
            return False

        return dict(result[0])

    async def delete_user(self, id):
        query = """
            DELETE FROM users
            WHERE id = $1
        """

        result = await db.db_query(
            query,
            id
        )

        return len(result) > 0
