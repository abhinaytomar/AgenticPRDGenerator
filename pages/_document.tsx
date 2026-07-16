import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <title>PRD Generator</title>
        <meta name="description" content="AI-powered Product Requirements Document generator" />
        <meta name="theme-color" content="#7c3aed" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}