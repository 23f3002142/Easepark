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
        <h1 class="text-4xl md:text-5xl font-bold tracking-tighter">Terms of Service</h1>
        <p class="text-sm font-mono text-gray-400 mt-6">Last updated: {{ lastUpdated }}</p>
      </div>
    </section>

    <!-- Body -->
    <section class="bg-white py-20">
      <div class="legal max-w-4xl mx-auto px-6 lg:px-8">
        <p class="lead">
          These Terms of Service ("Terms") govern your access to and use of EasePark ("the Service") at easepark.app.
          By creating an account or using the Service, you agree to these Terms. If you do not agree, do not use the Service.
        </p>

        <h2>1. The service</h2>
        <p>
          EasePark is a platform that helps drivers find, reserve, and pay for parking spots, and helps operators
          manage parking lots. We provide the technology that connects you with parking availability; we do not own
          or operate the parking lots themselves unless expressly stated.
        </p>

        <h2>2. Accounts</h2>
        <ul>
          <li>You must provide accurate information and keep your credentials secure.</li>
          <li>You are responsible for all activity that occurs under your account.</li>
          <li>You must be at least 18 years old, or have permission from a parent or guardian, to use the Service.</li>
          <li>Notify us immediately of any unauthorized use of your account.</li>
        </ul>

        <h2>3. Bookings and payments</h2>
        <ul>
          <li>When you reserve a spot, you agree to pay the displayed price for the time you park.</li>
          <li>Payments are processed securely through Razorpay. By paying, you also agree to Razorpay's terms.</li>
          <li>Prices, availability, and pricing rules are set by lot operators and may change.</li>
          <li>You are responsible for parking lawfully and following the rules of each parking location.</li>
        </ul>

        <h2>4. Releasing spots and refunds</h2>
        <p>
          You may release a booked spot from your dashboard. Charges are based on the time used according to the
          applicable pricing. Refunds, where offered, are handled on a case-by-case basis and may be subject to the
          operator's policy. Contact us if you believe you were charged in error.
        </p>

        <h2>5. Acceptable use</h2>
        <p>You agree not to:</p>
        <ul>
          <li>Use the Service for any unlawful, fraudulent, or abusive purpose.</li>
          <li>Attempt to gain unauthorized access to accounts, systems, or data.</li>
          <li>Interfere with, disrupt, or overload the Service or its infrastructure.</li>
          <li>Reverse engineer, scrape, or misuse the Service or its content.</li>
        </ul>

        <h2>6. Intellectual property</h2>
        <p>
          The EasePark name, logo, software, and content are owned by us or our licensors and are protected by
          applicable laws. You may not copy, modify, or distribute them without permission.
        </p>

        <h2>7. Service availability</h2>
        <p>
          We work to keep the Service reliable but do not guarantee uninterrupted or error-free operation.
          We may modify, suspend, or discontinue any part of the Service at any time.
        </p>

        <h2>8. Disclaimer and limitation of liability</h2>
        <p>
          The Service is provided "as is" without warranties of any kind. To the maximum extent permitted by law,
          EasePark is not liable for any indirect, incidental, or consequential damages, including loss of data,
          vehicles, or property, arising from your use of the Service.
        </p>

        <h2>9. Termination</h2>
        <p>
          We may suspend or terminate your account if you violate these Terms. You may stop using the Service and
          request account deletion at any time.
        </p>

        <h2>10. Changes to these terms</h2>
        <p>
          We may update these Terms from time to time. When we do, we will revise the "Last updated" date above.
          Continued use of the Service after changes take effect constitutes acceptance of the updated Terms.
        </p>

        <h2>11. Governing law</h2>
        <p>
          These Terms are governed by the laws of India, without regard to conflict-of-law principles. Any disputes
          shall be subject to the exclusive jurisdiction of the competent courts in India.
        </p>

        <h2>12. Contact us</h2>
        <p>
          Questions about these Terms? Reach us at
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
