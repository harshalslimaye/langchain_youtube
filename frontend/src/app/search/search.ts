import { Component } from "@angular/core";
import { Router } from "@angular/router";

@Component({
  selector: 'app-search',
  standalone: true,
  templateUrl: './search.html',
  styleUrl: './search.scss'
})
export class SearchComponent {
    constructor(private router: Router) {}

    load(videoUrl: string) {
        const match = videoUrl.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
        if (!match) {
            alert('Invalid YouTube URL');
            return;
        }
        const videoId = match[1];
        this.router.navigate([videoId]);
    }
}
