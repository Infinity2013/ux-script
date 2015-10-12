/**
 * Copyright (c) 2014 Qualcomm Technologies, Inc.  All Rights Reserved.
 * Qualcomm Technologies Proprietary and Confidential.
 */

var CryptoJSUtil = {

    secretPassphrase : "vellamo",

    iv : CryptoJS.enc.Hex.parse('000102030405060708090A0B0C0D0E0F'),

    decryptAES: function(encrypted) {
        return CryptoJS.AES.decrypt(encrypted, CryptoJSUtil.secretPassphrase, { mode: CryptoJS.mode.ECB, iv: CryptoJSUtil.iv, padding: CryptoJS.pad.NoPadding});
    },

    encryptAES: function(data) {
        return CryptoJS.AES.encrypt(data, CryptoJSUtil.secretPassphrase, { mode: CryptoJS.mode.ECB, iv: CryptoJSUtil.iv, padding: CryptoJS.pad.NoPadding});
    },

    //SHA2
    SHA256: function(data) {
      return CryptoJS.SHA256(data);
    },

};
