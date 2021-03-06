from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Question
from teams.forms import UploadFileForm
from teams.models import TeamCodingAnswer, Team, UploadFileModel

ALLOTTED_HOURS = 1


def _get_case_list(question):
    """
    Returns a list of cases.
    case:
        input:
            case_no
            case_text
        output:
            case_no
            field_name
    """
    case_list = []

    for inputcase in question.inputcase_set.all():
        case_list.append({
            'input': {
                'case_no': inputcase.case_no,
                'case_text': inputcase.case_text},
            'output': {
                'case_no': inputcase.case_no,
                'field_name': 'output_field-' + str(inputcase.case_no)}}
        )

    return case_list


def _get_question_statuses(team):
    """
    Returns a dictionary of Question numbers and statuses as key-value pairs.
    Status could be:
        'S': Solved
        'PS': Partially Solved
        'U': Unattempted
    """
    status_dict = {}

    for ques in Question.objects.all():
        answer_list = team.teamcodinganswer_set.filter(
            question_no=ques.question_no
        )

        if answer_list.exists():
            empty_count = 0
            for answer in answer_list:
                if answer.output_text == '':
                    empty_count += 1

            if empty_count == 0:
                status = 'S'
            elif empty_count == answer_list.count():
                status = 'U'
            else:
                status = 'PS'
        else:
            status = 'U'

        status_dict[ques.question_no] = status

    return status_dict


def _is_time_over(team):
    """
    Check if time exceeded the allotted limit.
    """
    # If `coding_start_time` is not NULL in db
    if team.coding_start_time is not None:
        time_diff = timezone.now() - team.coding_start_time

        if time_diff.total_seconds() > ALLOTTED_HOURS * 3600:
            return True

    return False


def _get_remaining_time(team):
    """
    Returns remaining time in seconds from allotted time.
    """
    # If `coding_start_time` is not NULL in db
    if team.coding_start_time is not None:
        time_diff = timezone.now() - team.coding_start_time
        remaining_time = ALLOTTED_HOURS * 3600 - time_diff.total_seconds()

        return remaining_time


@login_required
def index(request):
    team = get_object_or_404(Team, team_name=request.user)

    status_dict = _get_question_statuses(team)

    return render(request, 'coding/index.html', {
        'is_time_over': _is_time_over(team),
        'status_dict': status_dict,}
    )


@login_required
def challenge(request, question_no):
    question = get_object_or_404(Question, question_no=question_no)
    team = get_object_or_404(Team, team_name=request.user)

    # Save current time if `coding_start_time` is NULL in db
    if team.coding_start_time is None:
        team.coding_start_time = timezone.now()
        team.save()

    if _is_time_over(team):
        return HttpResponseRedirect(reverse('coding:index'))

    case_list = _get_case_list(question)
    status_dict = _get_question_statuses(team)



    if request.method == 'POST':

        file_form = UploadFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            # Save file
            obj, is_created = UploadFileModel.objects.update_or_create(
                team=team,
                question_no=question_no,
                defaults={'file': request.FILES['file'],}
            )

            # Save Output texts
            for case in case_list:
                output_field = case['output']['field_name']
                output_text = request.POST.get(output_field)

                obj, is_created = TeamCodingAnswer.objects.update_or_create(
                    question_no=question.question_no,
                    inputcase_no=case['input']['case_no'],
                    team=team,
                    defaults={'output_text': output_text,}
                )

            next_question_no = int(question_no) + 1
            if Question.objects.filter(question_no=next_question_no).exists():
                return HttpResponseRedirect(reverse('coding:challenge',
                                            args=(next_question_no,)))
            else:
                return HttpResponseRedirect(reverse('coding:index'))

    else:
        file_form = UploadFileForm()

    # Populate output text with previous answers
    for case in case_list:
        try:
            answer = team.teamcodinganswer_set.get(
                question_no=question_no,
                inputcase_no=case['input']['case_no']
            )
            case['output']['previous_answer'] = answer.output_text
        except TeamCodingAnswer.DoesNotExist:
            case['output']['previous_answer'] = ''


    return render(request, 'coding/challenge.html', {
        'question': question,
        'case_list': case_list,
        'status_dict': status_dict,
        'file_form': file_form,
        'remaining_time': _get_remaining_time(team),}
    )
