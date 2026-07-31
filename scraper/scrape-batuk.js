const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  console.log('Starting Batuk scraper...\n');

  const browser = await chromium.launch({
    headless: true,
    executablePath: '/opt/pw-browsers/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();
  const url = 'https://www.batuk.com.ar/hombre/abrigos/';

  console.log(`Navigating to ${url}`);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  } catch (error) {
    console.log('Page load warning:', error.message);
    console.log('Continuing anyway...');
  }

  console.log('Page loaded, taking screenshot...');
  await page.screenshot({ path: 'page-screenshot.png' });
  console.log('Screenshot saved: page-screenshot.png\n');

  // Scroll down to load all products (lazy loading)
  let previousHeight = 0;
  let retries = 0;
  const maxRetries = 20;

  console.log('Loading all products by scrolling...');
  while (retries < maxRetries) {
    const currentHeight = await page.evaluate(() => document.body.scrollHeight);

    if (currentHeight === previousHeight) {
      retries++;
      if (retries >= maxRetries) break;
      console.log(`No new content, retry ${retries}/${maxRetries}`);
      await page.waitForTimeout(1000);
    } else {
      retries = 0;
    }

    previousHeight = currentHeight;
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(500);
  }

  console.log('Extracting product data...\n');

  // Extract product data
  const products = await page.evaluate(() => {
    const items = document.querySelectorAll('[class*="product"]');
    const productList = [];

    // Try multiple selectors to find products
    const productElements = document.querySelectorAll(
      'a[href*="/producto/"], .product-item, [class*="card"], li[class*="item"]'
    );

    productElements.forEach((element) => {
      try {
        // Get URL
        let url = null;
        const link = element.querySelector('a[href*="/producto/"]') || element.closest('a');
        if (link && link.href) {
          url = link.href;
        } else if (element.href && element.href.includes('/producto/')) {
          url = element.href;
        }

        if (!url) return;

        // Get image
        const img = element.querySelector('img');
        let image = null;
        if (img) {
          image = img.src || img.getAttribute('data-src');
        }

        // Get price - try multiple selectors
        let price = null;
        const priceElement =
          element.querySelector('[class*="price"]') ||
          element.querySelector('[data-testid*="price"]') ||
          element.querySelector('.precio') ||
          element.querySelector('span');

        if (priceElement) {
          price = priceElement.textContent.trim();
        }

        // Get product name/title
        let title = null;
        const titleElement =
          element.querySelector('h2') ||
          element.querySelector('h3') ||
          element.querySelector('[class*="title"]') ||
          element.querySelector('[class*="name"]');

        if (titleElement) {
          title = titleElement.textContent.trim();
        } else if (img && img.alt) {
          title = img.alt;
        }

        if (url) {
          productList.push({
            title,
            price,
            image,
            url
          });
        }
      } catch (e) {
        // Skip on error
      }
    });

    return productList;
  });

  // Remove duplicates by URL
  const uniqueProducts = Array.from(new Map(products.map(p => [p.url, p])).values());

  console.log(`Found ${uniqueProducts.length} products\n`);

  // Display products
  uniqueProducts.forEach((product, index) => {
    console.log(`\n${index + 1}. ${product.title || 'N/A'}`);
    console.log(`   Price: ${product.price || 'N/A'}`);
    console.log(`   URL: ${product.url}`);
    console.log(`   Image: ${product.image || 'N/A'}`);
  });

  // Save to JSON
  const outputData = {
    url: url,
    timestamp: new Date().toISOString(),
    totalProducts: uniqueProducts.length,
    products: uniqueProducts
  };

  fs.writeFileSync('batuk-products.json', JSON.stringify(outputData, null, 2));
  console.log('\n\nData saved to batuk-products.json');

  // Save to CSV
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

  await context.close();
  await browser.close();
  console.log('\nScraper completed!');
})();
