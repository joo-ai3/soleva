/**
 * Soleva Platform Performance Testing Suite
 * Comprehensive load testing and performance monitoring
 */

const axios = require('axios');
const { performance } = require('perf_hooks');

// Configuration
const CONFIG = {
  baseUrl: process.env.TEST_BASE_URL || 'https://thesoleva.com',
  apiUrl: process.env.TEST_API_URL || 'https://thesoleva.com/api',
  concurrent: parseInt(process.env.CONCURRENT_USERS) || 10,
  duration: parseInt(process.env.TEST_DURATION) || 60, // seconds
  rampUp: parseInt(process.env.RAMP_UP_TIME) || 10, // seconds
};

// Test scenarios
const scenarios = [
  {
    name: 'Homepage Load',
    method: 'GET',
    url: '/',
    weight: 30, // 30% of traffic
  },
  {
    name: 'Products Page',
    method: 'GET',
    url: '/products',
    weight: 25,
  },
  {
    name: 'Product Detail',
    method: 'GET',
    url: '/product/1',
    weight: 20,
  },
  {
    name: 'API - Products List',
    method: 'GET',
    url: '/api/products/products/',
    weight: 15,
  },
  {
    name: 'API - Categories',
    method: 'GET',
    url: '/api/products/categories/',
    weight: 10,
  }
];

// Performance metrics
class PerformanceMetrics {
  constructor() {
    this.metrics = {
      requests: 0,
      successful: 0,
      failed: 0,
      responseTimeSum: 0,
      responseTimes: [],
      errors: [],
      throughput: 0,
      startTime: null,
      endTime: null
    };
  }

  recordRequest(responseTime, isSuccess, error = null) {
    this.metrics.requests++;
    this.metrics.responseTimeSum += responseTime;
    this.metrics.responseTimes.push(responseTime);
    
    if (isSuccess) {
      this.metrics.successful++;
    } else {
      this.metrics.failed++;
      if (error) {
        this.metrics.errors.push(error);
      }
    }
  }

  getAverageResponseTime() {
    return this.metrics.requests > 0 
      ? this.metrics.responseTimeSum / this.metrics.requests 
      : 0;
  }

  getPercentile(percentile) {
    if (this.metrics.responseTimes.length === 0) return 0;
    
    const sorted = [...this.metrics.responseTimes].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  getThroughput() {
    if (!this.metrics.startTime || !this.metrics.endTime) return 0;
    
    const durationSeconds = (this.metrics.endTime - this.metrics.startTime) / 1000;
    return this.metrics.requests / durationSeconds;
  }

  getErrorRate() {
    return this.metrics.requests > 0 
      ? (this.metrics.failed / this.metrics.requests) * 100 
      : 0;
  }

  generateReport() {
    const duration = this.metrics.endTime - this.metrics.startTime;
    
    return {
      summary: {
        totalRequests: this.metrics.requests,
        successful: this.metrics.successful,
        failed: this.metrics.failed,
        errorRate: `${this.getErrorRate().toFixed(2)}%`,
        duration: `${(duration / 1000).toFixed(2)}s`,
        throughput: `${this.getThroughput().toFixed(2)} req/s`
      },
      responseTime: {
        average: `${this.getAverageResponseTime().toFixed(2)}ms`,
        p50: `${this.getPercentile(50).toFixed(2)}ms`,
        p90: `${this.getPercentile(90).toFixed(2)}ms`,
        p95: `${this.getPercentile(95).toFixed(2)}ms`,
        p99: `${this.getPercentile(99).toFixed(2)}ms`,
        min: `${Math.min(...this.metrics.responseTimes).toFixed(2)}ms`,
        max: `${Math.max(...this.metrics.responseTimes).toFixed(2)}ms`
      },
      errors: this.metrics.errors.slice(0, 10) // Show first 10 errors
    };
  }
}

// Load test executor
class LoadTestExecutor {
  constructor() {
    this.metrics = new PerformanceMetrics();
    this.activeUsers = 0;
    this.isRunning = false;
  }

  async executeRequest(scenario) {
    const startTime = performance.now();
    const isApiRequest = scenario.url.startsWith('/api');
    const baseUrl = isApiRequest ? CONFIG.apiUrl : CONFIG.baseUrl;
    const url = baseUrl + scenario.url;

    try {
      const response = await axios({
        method: scenario.method,
        url: url,
        timeout: 30000,
        validateStatus: (status) => status < 500 // Only 5xx are failures
      });

      const endTime = performance.now();
      const responseTime = endTime - startTime;
      const isSuccess = response.status < 400;

      this.metrics.recordRequest(responseTime, isSuccess, 
        isSuccess ? null : `HTTP ${response.status}`);

      return { success: isSuccess, responseTime, status: response.status };
    } catch (error) {
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      this.metrics.recordRequest(responseTime, false, error.message);
      
      return { success: false, responseTime, error: error.message };
    }
  }

  selectScenario() {
    const random = Math.random() * 100;
    let cumulative = 0;
    
    for (const scenario of scenarios) {
      cumulative += scenario.weight;
      if (random <= cumulative) {
        return scenario;
      }
    }
    
    return scenarios[0]; // Fallback
  }

  async simulateUser() {
    while (this.isRunning) {
      const scenario = this.selectScenario();
      await this.executeRequest(scenario);
      
      // Random think time between 1-3 seconds
      const thinkTime = 1000 + Math.random() * 2000;
      await new Promise(resolve => setTimeout(resolve, thinkTime));
    }
  }

  async rampUpUsers() {
    const usersPerSecond = CONFIG.concurrent / CONFIG.rampUp;
    
    for (let i = 0; i < CONFIG.concurrent; i++) {
      this.simulateUser();
      this.activeUsers++;
      
      console.log(`🚀 Started user ${i + 1}/${CONFIG.concurrent}`);
      
      if (i < CONFIG.concurrent - 1) {
        await new Promise(resolve => 
          setTimeout(resolve, 1000 / usersPerSecond)
        );
      }
    }
  }

  async runLoadTest() {
    console.log('🔥 Starting Soleva Platform Load Test');
    console.log('=====================================');
    console.log(`📊 Configuration:`);
    console.log(`   Base URL: ${CONFIG.baseUrl}`);
    console.log(`   API URL: ${CONFIG.apiUrl}`);
    console.log(`   Concurrent Users: ${CONFIG.concurrent}`);
    console.log(`   Test Duration: ${CONFIG.duration}s`);
    console.log(`   Ramp-up Time: ${CONFIG.rampUp}s`);
    console.log('');

    this.isRunning = true;
    this.metrics.metrics.startTime = performance.now();

    // Start progress monitoring
    const progressInterval = setInterval(() => {
      const elapsed = (performance.now() - this.metrics.metrics.startTime) / 1000;
      const progress = (elapsed / CONFIG.duration) * 100;
      const current = this.metrics.generateReport();
      
      console.clear();
      console.log('🔥 Soleva Platform Load Test - In Progress');
      console.log('==========================================');
      console.log(`⏱️  Progress: ${progress.toFixed(1)}% (${elapsed.toFixed(1)}s / ${CONFIG.duration}s)`);
      console.log(`👥 Active Users: ${this.activeUsers}`);
      console.log(`📈 Requests: ${current.summary.totalRequests} (✅ ${current.summary.successful}, ❌ ${current.summary.failed})`);
      console.log(`⚡ Throughput: ${current.summary.throughput}`);
      console.log(`🕐 Avg Response Time: ${current.responseTime.average}`);
      console.log(`💥 Error Rate: ${current.summary.errorRate}`);
    }, 2000);

    // Ramp up users
    await this.rampUpUsers();

    // Run test for specified duration
    await new Promise(resolve => 
      setTimeout(resolve, CONFIG.duration * 1000)
    );

    // Stop test
    this.isRunning = false;
    this.metrics.metrics.endTime = performance.now();
    clearInterval(progressInterval);

    // Generate final report
    const report = this.metrics.generateReport();
    this.printReport(report);

    return report;
  }

  printReport(report) {
    console.clear();
    console.log('🏁 Soleva Platform Load Test - Complete!');
    console.log('=========================================');
    console.log('');
    
    console.log('📊 Test Summary:');
    console.log(`   Duration: ${report.summary.duration}`);
    console.log(`   Total Requests: ${report.summary.totalRequests}`);
    console.log(`   Successful: ${report.summary.successful}`);
    console.log(`   Failed: ${report.summary.failed}`);
    console.log(`   Error Rate: ${report.summary.errorRate}`);
    console.log(`   Throughput: ${report.summary.throughput}`);
    console.log('');
    
    console.log('⚡ Response Time Statistics:');
    console.log(`   Average: ${report.responseTime.average}`);
    console.log(`   50th Percentile: ${report.responseTime.p50}`);
    console.log(`   90th Percentile: ${report.responseTime.p90}`);
    console.log(`   95th Percentile: ${report.responseTime.p95}`);
    console.log(`   99th Percentile: ${report.responseTime.p99}`);
    console.log(`   Min: ${report.responseTime.min}`);
    console.log(`   Max: ${report.responseTime.max}`);
    console.log('');

    if (report.errors.length > 0) {
      console.log('❌ Sample Errors:');
      report.errors.slice(0, 5).forEach((error, index) => {
        console.log(`   ${index + 1}. ${error}`);
      });
      console.log('');
    }

    // Performance assessment
    this.assessPerformance(report);
  }

  assessPerformance(report) {
    console.log('🎯 Performance Assessment:');
    
    const avgResponseTime = parseFloat(report.responseTime.average);
    const errorRate = parseFloat(report.summary.errorRate);
    const throughput = parseFloat(report.summary.throughput);
    
    let score = 100;
    const issues = [];
    
    // Response time assessment
    if (avgResponseTime > 3000) {
      score -= 30;
      issues.push('❌ Average response time is too high (>3s)');
    } else if (avgResponseTime > 1000) {
      score -= 15;
      issues.push('⚠️  Average response time is high (>1s)');
    } else {
      issues.push('✅ Average response time is good (<1s)');
    }
    
    // Error rate assessment
    if (errorRate > 5) {
      score -= 40;
      issues.push('❌ Error rate is too high (>5%)');
    } else if (errorRate > 1) {
      score -= 20;
      issues.push('⚠️  Error rate is elevated (>1%)');
    } else {
      issues.push('✅ Error rate is acceptable (<1%)');
    }
    
    // Throughput assessment
    if (throughput < 10) {
      score -= 20;
      issues.push('⚠️  Throughput is low (<10 req/s)');
    } else {
      issues.push('✅ Throughput is good (≥10 req/s)');
    }
    
    issues.forEach(issue => console.log(`   ${issue}`));
    console.log('');
    console.log(`🏆 Overall Score: ${Math.max(0, score)}/100`);
    
    if (score >= 80) {
      console.log('🎉 Excellent performance! Ready for production.');
    } else if (score >= 60) {
      console.log('👍 Good performance with minor optimizations needed.');
    } else {
      console.log('⚠️  Performance needs improvement before production.');
    }
  }
}

// Health check function
async function healthCheck() {
  console.log('🏥 Running health checks...');
  
  const checks = [
    { name: 'Frontend', url: CONFIG.baseUrl },
    { name: 'API Health', url: `${CONFIG.apiUrl}/health/` },
    { name: 'Admin Panel', url: `${CONFIG.baseUrl}/admin/` }
  ];
  
  for (const check of checks) {
    try {
      const start = performance.now();
      const response = await axios.get(check.url, { timeout: 10000 });
      const responseTime = performance.now() - start;
      
      console.log(`✅ ${check.name}: ${response.status} (${responseTime.toFixed(2)}ms)`);
    } catch (error) {
      console.log(`❌ ${check.name}: ${error.message}`);
    }
  }
  console.log('');
}

// Main execution
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--health-only')) {
    await healthCheck();
    return;
  }
  
  // Run health check first
  await healthCheck();
  
  // Run load test
  const executor = new LoadTestExecutor();
  const report = await executor.runLoadTest();
  
  // Save report to file
  const fs = require('fs');
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportPath = `performance-report-${timestamp}.json`;
  
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`📄 Report saved to: ${reportPath}`);
  
  // Exit with appropriate code
  const errorRate = parseFloat(report.summary.errorRate);
  const avgResponseTime = parseFloat(report.responseTime.average);
  
  if (errorRate > 5 || avgResponseTime > 5000) {
    process.exit(1); // Performance test failed
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Test interrupted by user');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Test terminated');
  process.exit(0);
});

if (require.main === module) {
  main().catch(error => {
    console.error('💥 Test failed:', error.message);
    process.exit(1);
  });
}

module.exports = { LoadTestExecutor, PerformanceMetrics };
