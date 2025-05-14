import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject } from '../../interfaces/subject.interface';

@Component({
  selector: 'app-subject-card',
  templateUrl: './subject-card.component.html',
  styleUrls: ['./subject-card.component.scss'],
  standalone: true,
  imports: [CommonModule]
})
export class SubjectCardComponent {
  @Input() subject!: Subject;
  @Input() isSelected: boolean = false;
  @Output() selected = new EventEmitter<Subject>();

  onSelect(): void {
    this.selected.emit(this.subject);
  }
}
