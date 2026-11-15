// SPDX-License-Identifier: BSD-2-Clause-Patent
// Probe-only VerifiedRoot stubs for the fuxi UFS bring-up.
//
// The upstream ShengUfs driver links against the owner-verified block policy
// (verified_root_*, vr_*) and the boot-progress observer. The signed policy
// bundle those need is a Task 7 product (owner-signed per window); the probe
// (native-ufs-probe=2/3, register inspection and block reads) never reaches
// the root path. These definitions close the link honestly as disabled:
//
// - zero policy count: NativeUfsBlock::configureVerification returns on the
//   zero count before it reads the key, so verification is disabled rather
//   than approximated;
// - refusing vr_* entry points and a no-op progress observer: never called
//   by the probe path; any future root path fails closed.
//
// The IOBlockStorageDevice base comes from the pinned original imports
// (package/fuxi-storage-original-bindings.S), not from here.
#include <stddef.h>
#include <stdint.h>

#include "verified_root.h"       // kits/VerifiedRoot/include (upstream component)
#include "VerifiedBlockPolicy.h" // drivers/VirtioMmioBlock (upstream component)

extern "C" {

// NOTE: namespace-scope const has internal linkage in C++, which would leave
// these two undefined at link; the explicit extern gives them external linkage.
__attribute__((used)) extern const NativeVerifiedBlockPolicy verified_root_policies[1] = {};
__attribute__((used)) extern const uint64_t verified_root_policy_count = 0;
__attribute__((used)) extern const uint8_t verified_root_key[VR_KEY_BYTES] = {};
__attribute__((used)) extern const struct vr_crypto vr_xnu_crypto = {0, 0};

int
vr_open (const uint8_t *envelope, size_t envelopeBytes, const uint8_t key[VR_KEY_BYTES], uint64_t generation,
         const struct vr_crypto *crypto, struct vr_view *view)
{
  (void) envelope; (void) envelopeBytes; (void) key; (void) generation; (void) crypto; (void) view;
  return -1;
}

int
vr_open_header (const uint8_t *envelope, size_t envelopeBytes, const uint8_t key[VR_KEY_BYTES], uint64_t generation,
                const struct vr_crypto *crypto, struct vr_view *view)
{
  (void) envelope; (void) envelopeBytes; (void) key; (void) generation; (void) crypto; (void) view;
  return -1;
}

int
vr_verify_block (const struct vr_view *view, uint64_t index, const void *data, size_t length,
                 const struct vr_crypto *crypto)
{
  (void) view; (void) index; (void) data; (void) length; (void) crypto;
  return -1;
}

void
boot_progress_poll (void)
{
}

} // extern "C"
