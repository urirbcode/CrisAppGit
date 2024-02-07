from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from tabulate import tabulate

crisapp = Flask(__name__)
crisapp.secret_key = '123'

crisapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company_selection.db'
crisapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

crisdb = SQLAlchemy(crisapp)

class Team(crisdb.Model):
    id = crisdb.Column(crisdb.Integer, primary_key=True)
    name = crisdb.Column(crisdb.Text, nullable=False)
    seminar = crisdb.Column(crisdb.Integer, nullable=False)
    company = crisdb.Column(crisdb.Text, nullable=True)


with crisapp.app_context():
    crisdb.create_all()
    if not Team.query.first():  # Check if there is at least one entry in the Team table
        teams = [
            Team(name='Team 1', seminar=101, company=None),
            Team(name='Team 2', seminar=101, company=None),
            Team(name='Team 3', seminar=101, company=None),
            Team(name='Team 4', seminar=101, company=None),
            Team(name='Team 5', seminar=101, company=None),
            Team(name='Team 6', seminar=101, company=None),
            Team(name='Team 1', seminar=102, company=None),
            Team(name='Team 2', seminar=102, company=None),
            Team(name='Team 3', seminar=102, company=None),
            Team(name='Team 4', seminar=102, company=None),
            Team(name='Team 5', seminar=102, company=None),
            Team(name='Team 6', seminar=102, company=None),
            Team(name='Team 1', seminar=103, company=None),
            Team(name='Team 2', seminar=103, company=None),
            Team(name='Team 3', seminar=103, company=None),
            Team(name='Team 4', seminar=103, company=None),
            Team(name='Team 5', seminar=103, company=None),
            Team(name='Team 6', seminar=103, company=None)
        ]
        crisdb.session.add_all(teams)
        crisdb.session.commit()

allcompanies = ('France Telecom (Orange Telecom)', 'Boeing', 'Volkswagen', 'Amazon','Takara','Apple')

@crisapp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('select'))
    return render_template('base.html')

@crisapp.route('/select', methods=['GET', 'POST'])
def select():
    if request.method == 'POST':
        selected_seminar = request.form.get('seminar')
        selected_team = request.form.get('team')
        session['seminar'] = selected_seminar
        session['team'] = selected_team
        
        team_to_update = Team.query.filter(Team.seminar==session['seminar'], Team.name==session['team']).first()
        if team_to_update is not None:
            if team_to_update.company is not None:
                return redirect(url_for('already_selected'))
        return redirect(url_for('choice'))
    return render_template('select.html')


@crisapp.route('/choice', methods=['GET','POST'])
def choice():
    if request.method == 'GET':
        db_not_available_companies = Team.query.filter(Team.seminar==session['seminar'],Team.company.isnot(None)).with_entities(Team.company).all()
        not_available_companies = [company[0] for company in db_not_available_companies]
        available_companies = [co for co in allcompanies if co not in not_available_companies]
        return render_template('choice.html', available_companies=available_companies)
    elif request.method == 'POST':
        selected_company = request.form.get('company')
        session['company'] = selected_company
        
        team_to_update = Team.query.filter(Team.seminar==session['seminar'], Team.name==session['team']).first()
        
        if team_to_update is not None:
            team_to_update.company = session['company']
            crisdb.session.commit()
            return redirect(url_for('confirmation'))
        
        else:
            return "Team not found"

def generate_team_data_table():
    teams = Team.query.all()
    team_data = {(team.name, team.seminar, team.company) for team in teams}
    team_data = sorted(team_data, key=lambda x: (x[1], x[0]))
    table_header = ['Team', 'Seminar', 'Company']
    return tabulate(team_data, headers=table_header, tablefmt='html')

@crisapp.route('/confirmation')
def confirmation():
    html_table = generate_team_data_table()
    return render_template('confirmation.html', html_table=html_table)

@crisapp.route('/already_selected')
def already_selected():
    html_table = generate_team_data_table()
    return render_template('already_selected.html', html_table=html_table)


if __name__ == '__main__': 
    crisapp.run(debug=True)
    
