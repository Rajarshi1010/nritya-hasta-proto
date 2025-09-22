import { motion } from "framer-motion";

export default function Welcome() {
  return (
    <div className="welcome-page">
      <motion.header
        className="welcome-header"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="header-text">
          <h1 className="brand">NrityaLens</h1>
          <p className="tagline">
            Discover the beauty of Bharatanatyam through AI lens.
          </p>
        </div>


        {/* <div className="welcome-hero" aria-hidden="true"> */}
          <img src="./images/header.png" alt="Dancer silhouette" />
        {/* </div> */}
      </motion.header>


      <main className="main-grid">
        <motion.section
          className="section-card"
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7 }}
          viewport={{ once: true }}
        >
          <img src="./images/feature.png" alt="Bharatanatyam mudra" className="section-image" />

          <div style={{ display: 'flex', flexDirection: 'column', marginLeft: '3vw' }}>
            <h2>Features</h2>
            <ul>
              <li>Detect mudras from photos, videos, or live camera input.</li>
              <li>Learn about classical Bharatanatyam mudras with descriptions.</li>
              <li>Interactive, easy-to-use interface for all levels.</li>
              <li>Powered by AI gesture recognition models.</li>
              <li>Supports accessibility and high-contrast mode.</li>
            </ul>
          </div>
        </motion.section>


        <motion.aside
          className="section-card"
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7 }}
          viewport={{ once: true }}
        >
          <img src="/images/working.png" alt="Dance performance" className="section-image" />

          <div style={{ display: 'flex', flexDirection: 'column', marginLeft: '3vw' }}>
            <h2>How it Works</h2>
            <p>
              Upload a photo, record a video, or use your live camera feed. Our
              AI engine analyzes hand gestures and identifies the corresponding
              mudra with confidence levels and educational insights.
            </p>
            <a href='/dash' className="button-primary">Get Started</a>
          </div>
        </motion.aside>
      </main>


      <motion.footer
        className="welcome-footer"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9, duration: 0.8 }}
      />
        © {new Date().getFullYear()} NrityaLens • Preserve tradition with AI
    </div>
  );
}
