from models.models import reset_db, SessionLocal, Job
from merge.combine_all_jobs import combine_all_jobs

def load_data():
    combine_all_jobs()

if __name__ == '__main__':
    reset_db()
    load_data()
