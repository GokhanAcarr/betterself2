import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClientModule, HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule, HttpClientModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.scss']
})
export class LandingComponent {

  displayModal = false;
  modalTitle = '';
  modalText = '';

  constructor(private http: HttpClient) {}

  scrollToSection() {
    const element = document.getElementById('learn-more-section');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  openModal(type: 'mission' | 'team' | 'contact') {
    if (type === 'mission') {
      this.modalTitle = 'Our Mission';
      this.modalText = `
        <hr>
        <p>At BetterSelf, our mission is to empower individuals to achieve their health and fitness goals by combining cutting-edge technology with scientifically-backed methods. In today’s fast-paced world, maintaining a healthy lifestyle is more important and challenging than ever. We strive to provide tools that enable everyone to better understand and improve their body and mind.</p>

        <p>Our intelligent, intuitive, and user-friendly platform allows users to easily track their daily activities, boost their motivation with real-time feedback, and optimize their personal development. Key features include:</p>

        <ul>
          <li>Personalized workout plans and progress tracking</li>
          <li>Monitoring sleep quality and recovery</li>
          <li>Nutritional guidance and calorie management</li>
          <li>Scientific analysis of exercise data and personalized reports</li>
          <li>Social support features to strengthen motivation</li>
        </ul>

        <p>We are committed to continuous innovation, researching how technology can positively impact human health, and delivering the most up-to-date and effective solutions to our users. Our mission goes beyond creating an app — we aim to foster a culture of healthy, mindful living and help people feel stronger, happier, and more confident.</p>

        <p>With BetterSelf by your side every step of the way, we support you in building healthy habits, reaching your goals, and living a better life.</p>
      `;
    } else if (type === 'team') {
      this.modalTitle = 'Our Team';
      this.modalText = `
        <h3>Meet the Team Behind BetterSelf</h3>
        <hr>
        <h5>GÖKDENİZ AKBAL B2105.010072</h5>
        <h5>GÖKHAN ACAR B2205.010102</h5>
        <h5>KEREM KARATAŞ B2105.010067</h5>
      `;
    } else if (type === 'contact') {
      this.modalTitle = 'Contact Us';
      this.modalText = `
        <p>You can reach us via email at:</p>
        <p><a href="mailto:betterself@gmail.com" style="color:#65478F; font-weight: bold;">betterself@gmail.com</a></p>
        <button>
          <a href="https://mail.google.com" target="_blank" rel="noopener noreferrer" 
             style="color:#65478F; text-decoration: underline; cursor: pointer;">
            Open Gmail
          </a>
        </button>
      `;
    }
    this.displayModal = true;
  }

  closeModal() {
    this.displayModal = false;
  }
}
