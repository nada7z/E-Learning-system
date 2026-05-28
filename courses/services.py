from courses.models import Enrollment
from quizzes.models import Quiz, QuizAttempt
from assignments.models import Assignment, Submission


def can_student_complete_course(student, course):
    enrollment = Enrollment.objects.filter(
        student=student,
        course=course
    ).first()

    if not enrollment:
        return False, "Student is not enrolled."

    normal_quizzes = Quiz.objects.filter(
        course=course,
        is_final_exam=False,
        is_published=True
    )

    final_exam = Quiz.objects.filter(
        course=course,
        is_final_exam=True,
        is_published=True
    ).first()

    for quiz in normal_quizzes:
        passed_quiz = QuizAttempt.objects.filter(
            student=student,
            quiz=quiz,
            passed=True
        ).exists()

        if not passed_quiz:
            return False, f'Quiz "{quiz.title}" is not passed yet.'

    if not final_exam:
        return False, "Final exam does not exist yet."

    final_exam_passed = QuizAttempt.objects.filter(
        student=student,
        quiz=final_exam,
        passed=True
    ).exists()

    if not final_exam_passed:
        return False, "Final exam is not passed yet."

    enrollment.completed = True
    enrollment.progress_percentage = 100
    enrollment.save()

    return True, "Course completed successfully."