from sqlmodel import Session, select
from app.db.session import engine
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace
from app.models.board import Board
from app.models.column import Column


def create_initial_data():
    with Session(engine) as session:
        print("Checking for existing data...")

        # 1. Check if data already exists
        user = session.exec(select(User).where(User.username == "dev_user")).first()

        if not user:
            print("Creating Seed Data...")

            # Create User
            user = User(
                username="dev_user",
                email="dev@valoro.ai",
                hashed_password="hashed_secret",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            # Create Workspace
            workspace = Workspace(name="Pulse Development", owner_id=user.id)
            session.add(workspace)
            session.commit()
            session.refresh(workspace)

            # Create Board
            board = Board(title="Backend Sprint 1", workspace_id=workspace.id)
            session.add(board)
            session.commit()
            session.refresh(board)

            # Create Columns
            col_todo = Column(title="To Do", board_id=board.id, order=0)
            col_doing = Column(title="In Progress", board_id=board.id, order=1)
            col_done = Column(title="Done", board_id=board.id, order=2)

            session.add(col_todo)
            session.add(col_doing)
            session.add(col_done)
            session.commit()
            session.refresh(col_todo)

            print("\n--- SEED COMPLETE ---")
            print(f"User ID: {user.id}")
            print(f"Workspace ID: {workspace.id}")
            print(f"Board ID: {board.id}")
            print(f"Column ID (To Do): {col_todo.id} <--- USE THIS to create tasks")
        else:
            print("Data already exists. Skipping seed.")


if __name__ == "__main__":
    create_initial_data()
