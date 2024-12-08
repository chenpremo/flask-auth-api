"use strict";
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const expect = require("chai").expect;
const yaml = require('js-yaml');
const fs = require('fs');
const validUrl = require("valid-url");

let chai = require('chai');
const chaiHttp = require('chai-http');
chai.use(chaiHttp);

let env;
try {
    env = yaml.safeLoad(fs.readFileSync('env.yml', 'utf8'));
} catch (e) {
    console.log(e);
}

let BASE_URL = env.BASE_URL;

describe("", () => {
  before("Initializing …", async function() {
    this.timeout(10000);
    let wakeUp = true;
    let wakeUpLimit = setTimeout(function() {
      wakeUp = false;
    }, 5000);
    while(wakeUp) {
      await chai.request(BASE_URL)
        .get("/")
        .catch(function(res) {
            if (typeof res.response !== "undefined") {
            console.log("OK");
            wakeUp = false;
          }
        });
    }
  });

  describe("[Basic Case] codecheck.yml:", () => {
    it("BASE_URL has a valid URL.", () => {
      console.log(BASE_URL);
      // "記述されたURLが無効な形式です。"
      expect(validUrl.isUri(BASE_URL)).to.be.ok;
    });
  });

  describe("[Basic Case] API server:", () => {
    it("Accessing BASE_URL returns code 404.", function(done) {
       this.timeout(10000);
      chai.request(BASE_URL)
      .get("/")
      .catch(function (res) {
	expect(res.status).to.equal(404);
	done();
      });
    });
  });
});