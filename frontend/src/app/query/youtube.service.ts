import { inject, Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

interface ApiResponse {
  message: string;
  history?: { role: 'user' | 'assistant'; content: string }[];
}

@Injectable({
  providedIn: 'root'
})
export class YoutubeService {
  private prefix = 'http://127.0.0.1:8000/v01/rest/';
  private http = inject(HttpClient);

  load(videoId: string): Observable<ApiResponse> {
    return this.http.get<ApiResponse>(`${this.prefix}load/${videoId}`);
  }

  query(videoId: string, question: string): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.prefix}query/${videoId}`, { question });
  }
}
