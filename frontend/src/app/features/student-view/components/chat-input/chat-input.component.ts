import { Component, ElementRef, EventEmitter, Output, ViewChild, AfterViewInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface ChatMessageInput {
  text: string;
  file?: File;
}

export interface PredefinedPrompt {
  title: string;
  text: string;
  icon: string;
}

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-input.component.html',
  styleUrls: ['./chat-input.component.scss']
})
export class ChatInputComponent implements AfterViewInit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  @ViewChild('messageInput') messageInput!: ElementRef<HTMLTextAreaElement>;
  @Output() sendMessage = new EventEmitter<ChatMessageInput>();
  
  message: string = '';
  selectedFile: File | null = null;
  selectedFileName: string = '';
  showPromptMenu: boolean = false;

  // Prompts predefinidos
  predefinedPrompts: PredefinedPrompt[] = [
    {
      title: 'Crear Examen Completo',
      text: 'Crea un examen de 10 preguntas sobre los temas que hemos visto en la asignatura. Incluye 5 preguntas de opción múltiple, 3 de verdadero/falso y 2 de desarrollo.',
      icon: '📝'
    },
    {
      title: 'Resumen de Tema',
      text: 'Crea un resumen completo y estructurado de los temas principales que hemos estudiado en la asignatura.',
      icon: '📋'
    },
    {
      title: 'Ejercicios de Práctica',
      text: 'Genera ejercicios de práctica sobre los conceptos más importantes de la asignatura con sus respectivas soluciones.',
      icon: '🏋️'
    },
    {
      title: 'Mapa Conceptual',
      text: 'Elabora un mapa conceptual en formato texto que muestre las relaciones entre los conceptos principales de la asignatura.',
      icon: '🗺️'
    },
    {
      title: 'Guía de Estudio',
      text: 'Crea una guía de estudio organizada con los puntos clave, técnicas de memorización y recomendaciones para preparar el examen.',
      icon: '📚'
    },
    {
      title: 'Preguntas Frecuentes',
      text: 'Identifica y responde las preguntas más frecuentes sobre los temas de la asignatura que suelen tener los estudiantes.',
      icon: '❓'
    }
  ];

  ngAfterViewInit(): void {
    if (this.messageInput?.nativeElement) { 
      this.adjustTextareaHeight();
    }
  }
  
  @HostListener('input', ['$event.target'])
  onInput(textArea: HTMLTextAreaElement): void {
    this.adjustTextareaHeight();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.prompt-menu-container')) {
      this.showPromptMenu = false;
    }
  }

  adjustTextareaHeight(): void {
    const textarea = this.messageInput.nativeElement;
   
    textarea.style.height = 'auto';
    
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  onSubmit(): void {
    if (this.message.trim() || this.selectedFile) {
      this.sendMessage.emit({
        text: this.message.trim(),
        file: this.selectedFile || undefined
      });
      this.message = '';
      this.clearSelectedFile();
      
      setTimeout(() => {
        if (this.messageInput?.nativeElement) {
          this.messageInput.nativeElement.style.height = 'auto';
        }
      }, 0);
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.onSubmit();
    }
  }
  
  openFileSelector(): void {
    this.fileInput.nativeElement.click();
  }
  
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.selectedFileName = this.selectedFile.name;
    }
  }
  
  clearSelectedFile(): void {
    this.selectedFile = null;
    this.selectedFileName = '';
    if (this.fileInput?.nativeElement) {
      this.fileInput.nativeElement.value = '';
    }
  }

  togglePromptMenu(): void {
    this.showPromptMenu = !this.showPromptMenu;
  }

  selectPrompt(prompt: PredefinedPrompt): void {
    this.message = prompt.text;
    this.showPromptMenu = false;
    
    // Ajustar la altura del textarea después de establecer el mensaje
    setTimeout(() => {
      this.adjustTextareaHeight();
    }, 0);
  }
}
