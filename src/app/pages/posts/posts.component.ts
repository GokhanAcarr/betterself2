import { Component, OnInit } from '@angular/core';
import { PostService, Post } from '../../services/posts.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  standalone: true,
  imports: [FormsModule, CommonModule],
})
export class PostsComponent implements OnInit {
  posts: Post[] = [];
  newPost = { title: '', content: '' };

  constructor(private postService: PostService) {}

  ngOnInit(): void {
    this.loadPosts();
  }

  loadPosts(): void {
    this.postService.getPosts().subscribe({
      next: (data) => {
        this.posts = data;
      },
      error: (err) => {
        console.error('Postlar alınamadı:', err);
      },
    });
  }

  submitPost(event: Event): void {
    event.preventDefault();
    this.postService.createPost(this.newPost).subscribe({
      next: () => {
        this.newPost = { title: '', content: '' };
        this.loadPosts();
      },
      error: (err) => {
        console.error('Post paylaşımı başarısız:', err);
      },
    });
  }

  deletePost(postId: number): void {
    this.postService.deletePost(postId).subscribe({
      next: () => {
        this.loadPosts();
      },
      error: (err) => {
        console.error('Delete failed', err);
      },
    });
  }
}