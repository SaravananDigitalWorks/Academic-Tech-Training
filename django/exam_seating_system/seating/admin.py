from django.contrib import admin
from .models import ExamHall, Subject, Student, StudentSubjectMapping, Teacher, TeacherSubjectMapping, SeatingArrangement, SubjectExamHallMapping
import logging
logger = logging.getLogger(__name__)
from django.contrib import messages


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'contact_number', 'email', 'user')
    search_fields = ('name', 'roll_number')

@admin.register(StudentSubjectMapping)
class StudentSubjectMappingAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject')
    search_fields = ('student__name', 'subject__name')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'contact_number', 'email', 'user')

@admin.register(TeacherSubjectMapping)
class TeacherSubjectMappingAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject')
    search_fields = ('teacher__user__username', 'subject__name')

@admin.register(SeatingArrangement)
class SeatingArrangementAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam_hall', 'subject', 'row', 'seat')



@admin.register(SubjectExamHallMapping)
class SubjectExamHallMappingAdmin(admin.ModelAdmin):
    list_display = ('subject', 'exam_hall')
    search_fields = ('subject__name', 'exam_hall__name')

@admin.action(description="Map Seating Arrangement")
def map_seating_arrangement(modeladmin, request, queryset):
    for exam_hall in queryset:
        logger.info(f"Processing Exam Hall: {exam_hall.name}")  # Logging statement

        # Get all subjects mapped to the selected exam hall
        subject_mappings = exam_hall.subject_mappings.all()
        if not subject_mappings.exists():
            logger.warning(f"No subjects mapped to {exam_hall.name}. Skipping.")  # Logging statement
            continue

        students_by_subject = {}
        for mapping in subject_mappings:
            # Fetch students for the subject using StudentSubjectMapping
            student_mappings = StudentSubjectMapping.objects.filter(subject=mapping.subject)
            students = [sm.student for sm in student_mappings]
            if not students:
                logger.warning(f"No students found for subject {mapping.subject.name}. Skipping.")  # Logging statement
                continue
            students_by_subject[mapping.subject] = students

        if not students_by_subject:
            logger.warning(f"No students found for any subjects in {exam_hall.name}. Skipping.")  # Logging statement
            continue

        # Clear existing seating arrangements for the exam hall
        SeatingArrangement.objects.filter(exam_hall=exam_hall).delete()
        logger.info(f"Cleared existing seating arrangements for {exam_hall.name}.")  # Logging statement

        # Assign seats
        row = 1
        seat = 1
        while row <= exam_hall.rows:
            logger.info(f"Assigning seats for Row {row}...")  # Logging statement
            for subject, students in students_by_subject.items():
                if students:
                    student = students.pop(0)
                    SeatingArrangement.objects.create(
                        exam_hall=exam_hall,
                        subject=subject,
                        student=student,
                        row=row,
                        seat=seat
                    )
                    logger.info(f"Assigned {student.name} to Row {row}, Seat {seat}.")  # Logging statement
                    seat += 1
                    if seat > exam_hall.seats_per_row:
                        seat = 1
                        row += 1
                        if row > exam_hall.rows:
                            logger.info(f"Exam Hall {exam_hall.name} is full.")  # Logging statement
                            break  # Stop if the hall is full
                else:
                    logger.info(f"No more students for subject {subject.name}.")  # Logging statement
            else:
                logger.info("All subjects processed for this row.")  # Logging statement
                break  # Exit the loop if no more students are left
            if row > exam_hall.rows:
                break  # Exit the loop if the hall is full

    # Show a success message
    modeladmin.message_user(request, "Seating arrangement mapped successfully for selected exam halls.")

@admin.register(ExamHall)
class ExamHallAdmin(admin.ModelAdmin):
    list_display = ('name', 'rows', 'seats_per_row')
    actions = [map_seating_arrangement]