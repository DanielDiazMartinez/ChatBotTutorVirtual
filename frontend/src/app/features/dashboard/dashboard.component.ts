import { Component } from '@angular/core';
import { ChatInputComponent } from "./chat-input/chat-input.component";

@Component({
  selector: 'app-dashboard',
  imports: [ChatInputComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {

}
