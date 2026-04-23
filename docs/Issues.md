# Issues

## 1- englandsquash SSLCertVerificationError

```
2026-04-01 13:58:39,916  WARNING   Retrying (Retry(total=0, connect=0, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1020)'))': /openactive
2026-04-01 13:58:40,048  WARNING   HTTP 403 fetching: https://www.englandsquash.com/openactive
2026-04-01 13:58:40,048  ERROR     Cannot get dataset: https://www.englandsquash.com/openactive
```

Cloudflare is blocking the request. The server uses Cloudflare protection and is returning 403 for non-browser traffic.
This is a server-side WAF (Web Application Firewall) block — no amount of header changes will fix this. Cloudflare detects that it's not a real browser based on things like:
- Missing JavaScript execution
- TLS fingerprint (JA3/JA4)
- Missing cookies from previous page visits
This is expected behavior — some providers actively block automated access. Your code is handling it correctly by logging the error and continuing.

The only solutions would be:
- Contact England Squash to whitelist your IP/user-agent
- Use a browser automation tool like Playwright (much heavier)
- Accept that this feed is inaccessible via automated collection

THIS IS WORKING NOW???

## 2- Find My Facility feeds are empty 

## **** 3- Delete is slow

ingest-worker_1 is gone for 1 hour
 
2026-04-23 13:45:57,685  INFO      [ingest-worker_1] [dataset=https://better-admin.org.uk/api/openactive/better]  Persist start for dataset https://better-admin.org.uk/api/openactive/better: updates=118875 deletes=669733

## **** 4- Separate columns for activity and facility names




# Improvements 

1. In https://activeleeds-oa.leisurecloud.net/OpenActive/ locations are only names such as "Aireborough", "Pudsey", "Kippax"
Use ONS Index of Place Names to filter them and then https://api.postcodes.io/places?q={place_name} to get geolocations. Filtering is important otherwise we will get a lot of false positives.


*** Link to facility Ids?