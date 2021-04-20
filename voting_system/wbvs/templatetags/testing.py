from django import template
from wbvs.models import Result, User, Booth, Candidate, Voter, VotingList, History
register = template.Library()

@register.simple_tag
def show_image(candidate_id):
    return Candidate.objects.get(candidateID = candidate_id).image.url
    
@register.simple_tag
def show_name(candidate_id):
    return Candidate.objects.get(candidateID = candidate_id).candidateName