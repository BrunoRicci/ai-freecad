const fs = require('fs');
const { JSDOM } = require('jsdom');

(async () => {
  console.log('Starting Batuk scraper with DOM parsing...\n');

  const url = 'https://www.batuk.com.ar/hombre/abrigos/';

  try {
    console.log(`Fetching ${url}`);
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const html = await response.text();
    console.log(`Received ${html.length} bytes of HTML\n`);

    // Parse HTML with JSDOM
    const dom = new JSDOM(html, {
      url: url,
      pretendToBeVisual: true
    });

    const document = dom.window.document;
    const products = [];

    // Find all product items - try multiple selectors
    let productElements = document.querySelectorAll('[data-store^="product-item-"]');
    if (productElements.length === 0) {
      productElements = document.querySelectorAll('.js-item-product');
    }
    if (productElements.length === 0) {
      productElements = document.querySelectorAll('[class*="item-product"]');
    }

    console.log(`Found ${productElements.length} product containers\n`);

    productElements.forEach((element, index) => {
      try {
        // Get the product link
        const link = element.querySelector('a');
        let productUrl = null;
        if (link && link.href) {
          productUrl = link.href;
          // Make absolute URL
          if (!productUrl.startsWith('http')) {
            productUrl = new URL(productUrl, url).href;
          }
        }

        // Get product image - handle lazy loading
        let image = null;
        const img = element.querySelector('img');
        if (img) {
          // Try to get actual image, avoiding data URIs (lazy loading placeholders)
          image = img.src;
          if (!image || image.startsWith('data:')) {
            image = img.getAttribute('data-src') || img.getAttribute('data-original');
          }
          if (image && !image.startsWith('http') && !image.startsWith('data:')) {
            image = new URL(image, url).href;
          }
          // Avoid data URIs
          if (image && image.startsWith('data:')) {
            image = null;
          }
        }

        // Get product title/name
        let title = null;
        const titleElement = element.querySelector('h2, h3, .product-title, [class*="title"]');
        if (titleElement) {
          title = titleElement.textContent.trim();
        }
        if (!title && img) {
          title = img.alt || 'Product';
        }

        // Get product price - extract the first price value
        let price = null;
        const priceElement = element.querySelector('[class*="price"], .precio, [data-testid*="price"]');
        if (priceElement) {
          const priceText = priceElement.textContent.trim();
          // Extract just the price number (e.g., "$79.990,00" from larger text)
          const priceMatch = priceText.match(/\$[\d.,]+/);
          if (priceMatch) {
            price = priceMatch[0];
          } else {
            price = priceText.split('\n')[0].trim(); // Take first line if no $ found
          }
        }

        if (productUrl && title) {
          products.push({
            title,
            price: price || 'N/A',
            image: image || null,
            url: productUrl
          });

          console.log(`${index + 1}. ${title}`);
          console.log(`   Price: ${price || 'N/A'}`);
          console.log(`   URL: ${productUrl}`);
          console.log(`   Image: ${image || 'N/A'}\n`);
        }
      } catch (e) {
        console.error(`Error processing product ${index}:`, e.message);
      }
    });

    // Remove duplicates by URL, keeping the entry with the best data (with price)
    const uniqueMap = new Map();
    products.forEach(product => {
      const existing = uniqueMap.get(product.url);
      // Keep existing if it has a price and current doesn't, otherwise replace
      if (!existing || (product.price !== 'N/A' && existing.price === 'N/A')) {
        uniqueMap.set(product.url, product);
      }
    });
    const uniqueProducts = Array.from(uniqueMap.values());
    console.log(`Extracted ${products.length} products (${uniqueProducts.length} unique)\n`);

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

  } catch (error) {
    console.error('Error:', error.message);
  }

  console.log('\nScraper completed!');
})();
