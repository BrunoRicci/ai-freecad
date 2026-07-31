const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  console.log('Starting Batuk scraper with Playwright (headless)...\n');

  try {
    const browser = await chromium.launch({
      headless: true,
      executablePath: '/opt/pw-browsers/chromium',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled'
      ]
    });

    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1920, height: 1080 }
    });

    const page = await context.newPage();
    const url = 'https://www.batuk.com.ar/hombre/abrigos/';

    console.log(`Navigating to ${url}...`);
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    } catch (error) {
      console.log(`Navigation warning: ${error.message}`);
    }

    console.log('Waiting for products to load...');
    await page.waitForTimeout(2000);

    // Scroll to load lazy-loaded images
    console.log('Scrolling to load images...');
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.scrollBy(0, window.innerHeight));
      await page.waitForTimeout(500);
    }

    console.log('Taking screenshot...');
    await page.screenshot({ path: 'batuk-live.png' });

    console.log('Extracting product data from live page...\n');

    // Extract data from live page
    const products = await page.evaluate(() => {
      const items = [];
      const productElements = document.querySelectorAll('[data-store^="product-item-"]');

      productElements.forEach((element) => {
        try {
          // Get URL
          const link = element.querySelector('a[href]');
          if (!link) return;
          let url = link.href;

          // Get image
          let image = null;
          const img = element.querySelector('img');
          if (img) {
            image = img.src;
            // If src is data URI, try data-src or other attributes
            if (!image || image.startsWith('data:')) {
              image = img.getAttribute('data-src') ||
                      img.getAttribute('data-original') ||
                      img.srcset || null;
            }
            // Extract first URL from srcset if present
            if (image && image.includes(',')) {
              image = image.split(',')[0].trim().split(' ')[0];
            }
          }

          // Get title
          let title = null;
          const titleEl = element.querySelector('h2, h3, [class*="title"]');
          if (titleEl) {
            title = titleEl.textContent.trim();
          } else if (img && img.alt) {
            title = img.alt;
          }

          // Get price
          let price = null;
          const priceEl = element.querySelector('[class*="price"], .precio, [data-testid*="price"]');
          if (priceEl) {
            const text = priceEl.textContent.trim();
            const match = text.match(/\$[\d.,]+/);
            if (match) {
              price = match[0];
            }
          }

          if (url && title) {
            items.push({
              title,
              price: price || 'N/A',
              image: image || null,
              url
            });
          }
        } catch (e) {
          // Skip on error
        }
      });

      return items;
    });

    console.log(`Extracted ${products.length} total products\n`);

    // Deduplicate by URL, keeping entries with prices
    const uniqueMap = new Map();
    products.forEach(product => {
      const existing = uniqueMap.get(product.url);
      if (!existing || (product.price !== 'N/A' && existing.price === 'N/A')) {
        uniqueMap.set(product.url, product);
      }
    });
    const uniqueProducts = Array.from(uniqueMap.values());

    // Display results
    uniqueProducts.forEach((product, index) => {
      console.log(`${index + 1}. ${product.title}`);
      console.log(`   Price: ${product.price}`);
      console.log(`   URL: ${product.url}`);
      console.log(`   Image: ${product.image || 'N/A'}\n`);
    });

    console.log(`\nTotal: ${uniqueProducts.length} unique products\n`);

    // Save to JSON
    const outputData = {
      url: url,
      timestamp: new Date().toISOString(),
      totalProducts: uniqueProducts.length,
      products: uniqueProducts
    };

    fs.writeFileSync('batuk-products.json', JSON.stringify(outputData, null, 2));
    console.log('Data saved to batuk-products.json');

    // Save to CSV
    if (uniqueProducts.length > 0) {
      const csv = [
        ['Title', 'Price', 'URL', 'Image'].join(',')
      ].concat(
        uniqueProducts.map(p => [
          `"${(p.title || '').replace(/"/g, '""')}"`,
          `"${(p.price || '').replace(/"/g, '""')}"`,
          `"${(p.url || '').replace(/"/g, '""')}"`,
          `"${(p.image || '').replace(/"/g, '""')}"`
        ].join(','))
      ).join('\n');

      fs.writeFileSync('batuk-products.csv', csv);
      console.log('Data saved to batuk-products.csv');
    }

    await context.close();
    await browser.close();

    console.log('\nScraper completed!');

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
