from models.models import reset_db
from merge.combine_all_jobs import combine_all_jobs

if __name__ == '__main__':
    reset_db()
    combine_all_jobs()
    print("Database reset and data load complete.")