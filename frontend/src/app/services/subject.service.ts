import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Subject } from '../features/subject-selection/interfaces/subject.interface';

@Injectable({
  providedIn: 'root'
})
export class SubjectService {
  private selectedSubjectsSource = new BehaviorSubject<string[]>([]);
  selectedSubjects$ = this.selectedSubjectsSource.asObservable();

  setSelectedSubjects(subjects: string[]) {
    this.selectedSubjectsSource.next(subjects);
  }

  getSelectedSubjects() {
    return this.selectedSubjectsSource.value;
  }
}
