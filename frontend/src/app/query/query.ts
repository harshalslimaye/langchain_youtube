import { NgClass } from "@angular/common";
import { Component, inject, OnInit, signal } from "@angular/core";
import { ActivatedRoute, RouterLink } from '@angular/router';
import { YoutubeService } from './youtube.service';

interface Message {
  text: string;
  sender: 'user' | 'assistant';
  order: number;
}

@Component({
  selector: 'app-query',
  standalone: true,
  imports: [NgClass, RouterLink],
  templateUrl: './query.html',
  styleUrl: './query.scss'
})
export class QueryComponent implements OnInit {
  messages = signal<Message[]>([]);
  isTyping = signal(false);
  private route = inject(ActivatedRoute);
  private youtube = inject(YoutubeService);

  get videoId(): string {
    return this.route.snapshot.paramMap.get('videoId') || '';
  }

  ngOnInit(): void {
    this.isTyping.set(true);
    this.youtube.load(this.videoId).subscribe({
      next: (res) => this.pushMessage(res.message, 'assistant'),
      error: () => this.pushMessage('Failed to load video data.', 'assistant')
    });
  }

  sendMessage(input: HTMLInputElement) {
    this.pushMessage(input.value, 'user');
    this.isTyping.set(true);
    this.youtube.query(this.videoId, input.value).subscribe({
      next: (res) => this.pushMessage(res.message, 'assistant'),
      error: () => this.pushMessage('Failed to get a response.', 'assistant')
    });
    input.value = '';
  }

  private pushMessage(text: string, sender: 'user' | 'assistant') {
    this.isTyping.set(false);
    this.messages.update(msgs => [...msgs, { text, sender, order: msgs.length }]);
  }
}
