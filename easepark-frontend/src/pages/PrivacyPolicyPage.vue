<script setup lang="ts">
import PublicPageLayout from '@/components/PublicPageLayout.vue'

const lastUpdated = 'July 8, 2026'
</script>

<template>
  <PublicPageLayout>
    <!-- Header -->
    <section class="bg-black text-white border-b-2 border-black">
      <div class="max-w-4xl mx-auto px-6 lg:px-8 py-20">
        <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-4">Legal</p>
        <h1 class="text-4xl md:text-5xl font-bold tracking-tighter">Privacy Policy</h1>
        <p class="text-sm font-mono text-gray-400 mt-6">Last updated: {{ lastUpdated }}</p>
      </div>
    </section>

    <!-- Body -->
    <section class="bg-white py-20">
      <div class="legal max-w-4xl mx-auto px-6 lg:px-8">
        <p class="lead">
          This Privacy Policy explains how EasePark ("we", "us", "our") collects, uses, and protects your
          information when you use our website and services at easepark.app. By using EasePark, you agree to
          the practices described below.
        </p>

        <h2>1. Information we collect</h2>
        <ul>
          <li><strong>Account information</strong> — your name, username, and email address when you register (directly or via Google Sign-In).</li>
          <li><strong>Vehicle information</strong> — vehicle details you add to book and manage parking spots.</li>
          <li><strong>Booking &amp; usage data</strong> — the lots you view, spots you reserve, booking times, and history.</li>
          <li><strong>Payment information</strong> — payments are processed by Razorpay. We do <strong>not</strong> store your card, UPI, or bank details on our servers; we only retain transaction references and receipts.</li>
          <li><strong>Location data</strong> — approximate location you provide or select on the map to find nearby parking. We do not track your location in the background.</li>
          <li><strong>Technical data</strong> — basic request metadata (such as a request ID) needed to operate and secure the service.</li>
        </ul>

        <h2>2. How we use your information</h2>
        <ul>
          <li>To create and manage your account and authenticate you securely.</li>
          <li>To let you search, reserve, release, and pay for parking spots.</li>
          <li>To send transactional emails such as OTP verification, password resets, and booking confirmations.</li>
          <li>To show your history, receipts, and usage analytics on your dashboard.</li>
          <li>To operate, maintain, secure, and improve the service.</li>
        </ul>

        <h2>3. How we store and protect data</h2>
        <p>
          Authentication uses signed JSON Web Tokens (JWT). Your session token is stored locally in your browser,
          not in server-side cookies. Passwords are hashed and never stored in plain text. Access to your account
          requires email OTP verification. All traffic to easepark.app and our API is served over HTTPS.
        </p>

        <h2>4. Third-party services</h2>
        <p>We rely on trusted third parties to deliver the service. Each has its own privacy policy:</p>
        <ul>
          <li><strong>Razorpay</strong> — payment processing.</li>
          <li><strong>Google</strong> — optional Google Sign-In (OAuth).</li>
          <li><strong>Email provider</strong> — delivery of transactional emails (OTP, password reset, confirmations).</li>
          <li><strong>Hosting providers</strong> — our frontend and backend are hosted on cloud platforms that process data on our behalf.</li>
        </ul>

        <h2>5. Cookies and local storage</h2>
        <p>
          EasePark uses your browser's local storage to keep you signed in. We do not use third-party advertising
          or tracking cookies.
        </p>

        <h2>6. Data retention</h2>
        <p>
          We retain your account and booking information for as long as your account is active or as needed to
          provide the service and comply with legal obligations. You may request deletion of your account at any time.
        </p>

        <h2>7. Your rights</h2>
        <p>
          You may access, update, or delete your personal information from your profile, or by contacting us. You may
          also request a copy of the data we hold about you, or ask us to stop processing it, subject to applicable law.
        </p>

        <h2>8. Children's privacy</h2>
        <p>
          EasePark is not directed to children under 13, and we do not knowingly collect personal information from them.
        </p>

        <h2>9. Changes to this policy</h2>
        <p>
          We may update this Privacy Policy from time to time. When we do, we will revise the "Last updated" date above.
          Continued use of the service after changes take effect constitutes acceptance of the updated policy.
        </p>

        <h2>10. Contact us</h2>
        <p>
          If you have questions about this Privacy Policy or your data, contact us at
          <a href="mailto:support.easepark@gmail.com">support.easepark@gmail.com</a>.
        </p>
      </div>
    </section>
  </PublicPageLayout>
</template>

<style scoped>
.legal .lead {
  font-size: 1.125rem;
  line-height: 1.8;
  color: #374151;
  font-weight: 300;
  margin-bottom: 2.5rem;
  padding-bottom: 2.5rem;
  border-bottom: 2px solid #000;
}
.legal h2 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #000;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
}
.legal p {
  font-size: 1rem;
  line-height: 1.75;
  color: #374151;
  margin-bottom: 1rem;
}
.legal ul {
  list-style: none;
  margin: 0 0 1rem;
  padding: 0;
}
.legal li {
  position: relative;
  padding-left: 1.5rem;
  font-size: 1rem;
  line-height: 1.7;
  color: #374151;
  margin-bottom: 0.75rem;
}
.legal li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.6em;
  width: 0.5rem;
  height: 0.5rem;
  background: #000;
}
.legal strong { color: #000; font-weight: 600; }
.legal a {
  color: #000;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.legal a:hover { color: #4b5563; }
</style>
