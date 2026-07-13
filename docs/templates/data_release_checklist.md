# Data Release and Anonymization Checklist

Before publishing any benchmark data to a public repository (e.g., Zenodo, Hugging Face), complete this checklist to ensure compliance with privacy and site-permission rules.

## 1. Site Permissions
- [ ] Explicit written permission obtained from the facility/plant owner to publish 3D scans of the site.
- [ ] Any restricted areas within the site have been entirely cropped out of the raw point clouds and images.

## 2. Personal Identifiable Information (PII)
- [ ] RGB images run through a face-blurring algorithm.
- [ ] RGB images run through a license-plate-blurring algorithm (if vehicles are present).
- [ ] Point clouds manually inspected to remove any high-density clusters resembling human figures or operators.

## 3. Metadata Sanitization
- [ ] GPS coordinates removed from the scan manifest unless explicitly authorized for release.
- [ ] Internal project codes or proprietary pipe part numbers replaced with generic identifiers (e.g., `pipe_001`).

## 4. Ground Truth Integrity
- [ ] Ensure that no synthetic points were injected to "fix" ground truth. 
- [ ] Verify that measurement uncertainty columns are fully populated in the public release.

## Sign-off
**Reviewer Name:**
**Date:**
