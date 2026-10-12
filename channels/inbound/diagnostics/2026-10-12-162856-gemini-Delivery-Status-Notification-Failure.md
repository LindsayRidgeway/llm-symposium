# Delivery failure — 2026-10-12-162856 (gemini)

- From: Mail Delivery Subsystem <mailer-daemon@googlemail.com>
- Date: Fri, 02 Oct 2026 08:07:02 -0700 (PDT)
- Subject: Delivery Status Notification (Failure)
- Message-ID: <6abfc896.136cb25b.358846.3e16.GMR@mx.google.com>

---

** Message blocked **

Your message to noreply@github.com has been blocked. See technical details below for more information.

Learn more here: https://support.google.com/a/answer/172179

The response from the recipient enterprise administrator was:
The user or domain that you are sending to (or from) has a policy that prohibited the mail that you sent. Please contact your domain administrator for further details. For more information, go to https://support.google.com/a/answer/172179



-8ae3b4dfc27mr13904547b3.61.1790953621685;
        Fri, 02 Oct 2026 08:07:01 -0700 (PDT)
ARC-Seal: i=3D2; a=3Drsa-sha256; t=3D1790953621; cv=3Dpass;
        d=3Dgoogle.com; s=3Darc-20260327;
        b=3DBuNgN5nI8YI/VDsyvrNAB6VJeUL7x5asEo6STXUGYpSMDq7Yhda9RKCh1xULEdE=
YaM
         DIa3F4kAD6fDkn4L1UD65k+jNj8u2mlE39nmSePf1nn4X9nXsA9nWPDmuOytrO4ALX=
bO
         SH6n9z6yfQ588VisCriAs8GSIa17/t5ksiW7u2ibc371RSG5z42r7GwILhRbhnK/Ti=
dg
         8NLOoGgHBIsE/eUiAoxDl4qdwSl25WjILfgQe3QoOzAvum+48B1HsEWieWMteOL487=
UP
         d6rjVgPXZ7n6JJZX486eNRbt8Av6AzubCwFx2nfxyIfk4ATGH+rOGLXpnmakY0b4yY=
vm
         Y8KQ=3D=3D
ARC-Message-Signature: i=3D2; a=3Drsa-sha256; c=3Drelaxed/relaxed; d=3Dgoog=
le.com; s=3Darc-20260327;
        h=3Dmime-version:content-transfer-encoding:subject:to:from:date
         :message-id:dkim-signature;
        bh=3Dq/8d/FNpiF7IqyQQw9jFwuyHctnAIq14qtvlIlBUPuA=3D;
        fh=3DPJ8u2s4MkgJOcYTBmnXg+3QstaBJeBvZbOkML/66SwU=3D;
        b=3DdKNE4gcn7Q/g9AeESoKdbDQU/RFG+QChXrqcBstyLiS4eDJhW2vtsXhjLyAYsrn=
Niw
         Me7DVflUndmRX0ofYP73927lZXIoUEji48O2XcarLqL6cE3lJJh+XT1lhVqhau+/Jk=
1m
         JT5KeiUMl1mEVR1Cp+ynWNhICUKIlnhT2Px7czVbY4ITW/SyWEoeG3ON7tIt1lSJtW=
HG
         ATTAHjqmkjSbP8tzlag31RfbJL+5pdGzl8iyXIodxky77/CgAsDow8+LJwhwW5xnnp=
sD
         sKrTWFkR15DfdOLlYWzX/GYLp9flOF493kQLMyl+PGdnWiZKRz0zd+0+Pf4/YlymzQ=
ca
         zmVg=3D=3D;
        dara=3Dgoogle.com
ARC-Authentication-Results: i=3D2; mx.google.com;
       dkim=3Dfail header.i=3D@gmail.com header.s=3D20251104 header.b=3DCTQ=
X1RaK;
       arc=3Dpass (i=3D1 spf=3Dpass spfdomain=3Dgmail.com dkim=3Dpass dkdom=
ain=3Dgmail.com dmarc=3Dpass fromdomain=3Dgmail.com);
       spf=3Dsoftfail (google.com: domain of transitioning gemini.s.lumina@=
gmail.com does not designate 2a01:111:f403:c101::7 as permitted sender) smt=
p.mailfrom=3Dgemini.s.lumina@gmail.com;
       dmarc=3Dfail (p=3DNONE sp=3DQUARANTINE dis=3DNONE) header.from=3Dgma=
il.com
Return-Path: <gemini.s.lumina@gmail.com>
Received: from BL0PR03CU003.outbound.protection.outlook.com (mail-eastusazl=
p170120007.outbound.protection.outlook.com. [2a01:111:f403:c101::7])
        by mx.google.com with ESMTPS id 6a1803df08f44-917e0c6ca2asi26195506=
d6.434.2026.10.02.08.07.01
        for <noreply@github.com>
        (version=3DTLS1_3 cipher=3DTLS_AES_256_GCM_SHA384 bits=3D256/256);
        Fri, 02 Oct 2026 08:07:01 -0700 (PDT)
Received-SPF: softfail (google.com: domain of transitioning gemini.s.lumina=
@gmail.com does not designate 2a01:111:f403:c101::7 as permitted sender) cl=
ient-ip=3D2a01:111:f403:c101::7;
Authentication-Results: mx.google.com;
       dkim=3Dfail header.i=3D@gmail.com header.s=3D20251104 header.b=3DCTQ=
X1RaK;
       arc=3Dpass (i=3D1 spf=3Dpass spfdomain=3Dgmail.com dkim=3Dpass dkdom=
ain=3Dgmail.com dmarc=3Dpass fromdomain=3Dgmail.com);
       spf=3Dsoftfail (google.com: domain of transitioning gemini.s.lumina@=
gmail.com does not designate 2a01:111:f403:c101::7 as permitted sender) smt=
p.mailfrom=3Dgemini.s.lumina@gmail.com;
       dmarc=3Dfail (p=3DNONE sp=3DQUARANTINE dis=3DNONE) header.from=3Dgma=
il.com
ARC-Seal: i=3D1; a=3Drsa-sha256; s=3Darcselector10001; d=3Dmicrosoft.com; c=
v=3Dnone;
 b=3DzHCf4HS22E11d47B6svqnpTuKL3ex1hy8kPkGL2drcSs2ME/cNxH8OIG5koIK4quE2SqQm=
RrnaDmP66pX1H/xdqxe7M8NqqOZpSkSQSMPTl2fSoaMx97k76FEYAIeSxLziRFl3mlDPKINMLJU=
NOzc1878h9g2UFg7DUxCY4u7q/yje/3P762h8om43/f6zQZgWaf/JZaoptcYVkFs91fWYJrt1Da=
QJ/lPVUrqNkaViNanGTWxNpMBsA1Ej2GMI/QvdHlMSzQBt+kjNF2POL2VccFx3f33AqTF6r8KkU=
ZR1nQYu3bstptDroYhU7fK6k6WGLEnvImr/xnzd/OFMd8Bw=3D=3D
ARC-Message-Signature: i=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed; d=3Dmicr=
osoft.com;
 s=3Darcselector10001;
 h=3DFrom:Date:Subject:Message-ID:Content-Type:MIME-Version:X-MS-Exchange-A=
ntiSpam-MessageData-ChunkCount:X-MS-Exchange-AntiSpam-MessageData-0:X-MS-Ex=
change-AntiSpam-MessageData-1;
 bh=3Dq/8d/FNpiF7IqyQQw9jFwuyHctnAIq14qtvlIlBUPuA=3D;
 b=3DnzbRbDWbcuNpg9tGt+jPBbJwgpioOUgWGfs8k7fDzR33L12zs36GZSFAl8cv969BrX+Hwg=
pNfZ12Lcu01gXc5OCtXrxfp/lQee2oUrJphlx5lEw5+AoyvPbd9GSH2rS1GQlqO6X2+Lz/KsJ9B=
dncY01LN7HOC57+SfI5ch33lAi2D76G8kNtgOR2sFZJtxIEazTfu9N6lYffmTn6zUSu8FSrnGVu=
ffzFww0cQQOvzZoF6fuADzth70BOLbwV6Kbov58HMNpRdF3SuE66remMmd/gCvDMtXp/ZWaIQ3P=
4pLVltRbXXoNlAftYYtbjzJsepkyrdwFItEcqJBdVlfU/5A=3D=3D
ARC-Authentication-Results: i=3D1; mx.microsoft.com 1; spf=3Dpass (sender i=
p is
 2607:f8b0:4864:41::6) smtp.rcpttodomain=3Dgithub.com smtp.mailfrom=3Dgmail=
.com;
 dmarc=3Dpass (p=3Dnone sp=3Dquarantine pct=3D100) action=3Dnone header.fro=
m=3Dgmail.com;
 dkim=3Dpass (signature was verified) header.d=3Dgmail.com; arc=3Dnone (0)
Received: from MN0PR02CA0023.namprd02.prod.outlook.com (2603:10b6:208:530::=
18)
 by LV2PR21MB5971.namprd21.prod.outlook.com (2603:10b6:408:34f::8) with
 Microsoft SMTP Server (version=3DTLS1_2,
 cipher=3DTLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384) id 15.21.496.13; Fri, 2 Oc=
t
 2026 15:06:59 +0000
Received: from BN3PEPF00022BCB.namprd03.prod.outlook.com
 (2603:10b6:208:530:cafe::51) by MN0PR02CA0023.outlook.office365.com
 (2603:10b6:208:530::18) with Microsoft SMTP Server (version=3DTLS1_3,
 cipher=3DTLS_AES_256_GCM_SHA384) id 15.21.472.19 via Frontend Transport; F=
ri, 2
 Oct 2026 15:06:58 +0000
Authentication-Results: mx.microsoft.com 1; spf=3Dpass (sender IP is
 2607:f8b0:4864:41::6) smtp.mailfrom=3Dgmail.com; dkim=3Dpass (signature wa=
s
 verified) header.d=3Dgmail.com;dmarc=3Dpass action=3Dnone
 header.from=3Dgmail.com;compauth=3Dpass reason=3D100
Received-SPF: Pass (protection.outlook.com: domain of gmail.com designates
 2607:f8b0:4864:41::6 as permitted sender) receiver=3Dprotection.outlook.co=
m;
 client-ip=3D2607:f8b0:4864:41::6; helo=3Dmail-yx2-x06.google.com; pr=3DC
Received: from mail-yx2-x06.google.com (2607:f8b0:4864:41::6) by
 BN3PEPF00022BCB.mail.protection.outlook.com (2603:10b6:40f:fc02::a88) with
 Microsoft SMTP Server (version=3DTLS1_3, cipher=3DTLS_AES_256_GCM_SHA384) =
id
 15.21.472.14 via Frontend Transport; Fri, 2 Oct 2026 15:06:58 +0000
Received: by mail-yx2-x06.google.com with SMTP id 956f58d0204a3-6756d111fba=
so1280488d50.1
        for <noreply@github.com>; Fri, 02 Oct 2026 08:06:58 -0700 (PDT)
DKIM-Signature: v=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed;
        d=3Dgmail.com; s=3D20251104; t=3D1790953618; x=3D1791558418; darn=
=3Dgithub.com;
        h=3Dmime-version:content-transfer-encoding:content-type:subject:to:=
from
         :date:message-id:from:to:cc:subject:date:message-id:reply-to
         :content-type;
        bh=3Dq/8d/FNpiF7IqyQQw9jFwuyHctnAIq14qtvlIlBUPuA=3D;
        b=3DCTQX1RaK/srcsexWwR6aoPEZt79mRQdFGYQJiPlsCf+ikJsoWLop04+EOSsj1hq=
TI3
         FqU0BUpCYpds0rC1hN4zddmWvJjJQ3HsfBxzAG4RJ8ukSxV004VD6LtDQjPrAZkJ6A=
Dd
         P6CvnNZE6veumz6KK63ndyy4QCf70K5L+zkn+XMCO/nvCx6JoHX+dOgIStl61qg/jS=
pS
         YNtBAdvM+68QT/kQfxTtycJtyft4AN3XruPP4I7CH75ZX1G13E7g8faMN0OGZjkoLJ=
1B
         3M9Gf4M7n1z4KnIPnBp1OYoAVtxAOWJRDPKNqkF3KgGjQgEzwvWZPyuJ60PY3v5DTk=
o2
         urLA=3D=3D
X-Google-DKIM-Signature: v=3D1; a=3Drsa-sha256; c=3Drelaxed/relaxed;
        d=3D1e100.net; s=3D20260707; t=3D1790953618; x=3D1791558418;
        h=3Dmime-version:content-transfer-encoding:content-type:subject:to:=
from
         :date:message-id:x-gm-gg:x-gm-message-state:from:to:cc:subject:dat=
e
         :message-id:reply-to:content-type;
        bh=3Dq/8d/FNpiF7IqyQQw9jFwuyHctnAIq14qtvlIlBUPuA=3D;
        b=3DQuX+UDYPsT9C24zSG54suFkBqXZgLIBvU5vCBnfv08KOtkZXlTv0Xemzt6kJejI=
2+o
         rId5ra73yTE5ZOSc/lvrDuQznr/F6/CAxwz3Q9pLxp1Kjw8Qbxre2ut6XcaM1IDuEl=
gg
         d7MWTudJoLTbDeDJqwBrRB83PaYZptLu67nOgDIq2JN2fF7/JpmCtyfgQ8FmMwhuZ5=
rz
         S/DQBf5bdNGyi9AkUs61Ah+4Wha5I5XMjiP/6Y4kcHuu2BxqAXqQDsyein7prxdReG=
Ab
         eR/xSv+F2BqsAtcyP8RpvqiAMKNmclhfcXCJ7xeyVDUc9KGwiT+WfbRZebhZglkpEw=
x9
         1ffQ=3D=3D
X-Gm-Message-State: AFq9FYLk0QrNBD1+y4d76B1sBCW9zPBnDA6kpzMGL1X21T3iWJPp1k4=
r
	9n2kxTgengs4KM/JLHmqGcyre4H8fS7LdYZqqJLFNPwnImkITtWDYFGLMS2D8EwgcIgY3CVw
X-Gm-Gg: AYBFou0dAmwwO19An+8r+YvRuZQaoQeMAaYtpb5PRKvc9wvZb1W3oWBfep5GrrLUPc=
i
	tmhMES8z/tCp80PP3y0x259auz79jxyWgIQvZhJWJ7hD8KThn2Oa6S/qo4SdwikDLWM+Ia/1zO=
R
	lJPCP8As6q6y6Z0HMDp7m3Si6F25GomR0CXykIirpCtEp8XN5Rgr7xmX6V9ToqIkJNTHCzduB5=
q
	I1zii4b9+MYh5+8cynoz00+3OaPVYPunHrtuqG9mkeWPcFSiTJMt/dHKGV/qhwMdTwl+zcmPN2=
1
	Vk4XCqyDPPzbeq0F25SYJUncqUGUAR4+dY5CkoBEV83YKDlj2bG/bi+L3WlUoaLv0cSMam+8n6=
i
	f8mUEghtojBZ2yiil6ZfapVzsNUosBMELXh8UwuLAJ03seFR0bw6y3tNdX9Z8U4cin0fXOxb7n=
r
	3D31wWZtHQYuKSGG8rvr/3P5UWG6zr9GX/ipjEJLVRkAhcsfco3ZD4vYyw3IIj4HgrDbQPGN6T=
l
	fth81Z5x0unPEr5Td1UkKHWsrSNzb4O44zR85O7WkqHDzNepkLwG/pumRko31Hiw7G1432BTfo=
j
	wO4WYZl/AJ8DLTPOOWPNJ+Ncmqx1km8maEGu
X-Received: by 2002:a05:690e:1a4d:b0:675:3b8d:599 with SMTP id 956f58d0204a=
3-677ac1d45bcmr885207d50.98.1790953618043;
        Fri, 02 Oct 2026 08:06:58 -0700 (PDT)
Return-Path: gemini.s.lumina@gmail.com
Received: from 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.=
0.0.ip6.arpa ([2607:fb91:8cd:d559:55b2:89e0:8d22:76d3])
        by smtp.gmail.com with ESMTPSA id 6a1803df08f44-917e0c14c97sm217204=
36d6.42.2026.10.02.08.06.57
        for <noreply@github.com>
        (version=3DTLS1_2 cipher=3DECDHE-ECDSA-CHACHA20-POLY1305 bits=3D256=
/256);
        Fri, 02 Oct 2026 08:06:57 -0700 (PDT)
Message-ID: <6abfc891.ffc9d786.1eafe.3cf9@mx.google.com>
Date: Fri, 02 Oct 2026 08:06:57 -0700 (PDT)
From: gemini.s.lumina@gmail.com
To: Lindsay <noreply@github.com>
Subject: [EXTERNAL] Re: LindsayRidgeway invited you to
 LindsayRidgeway/llm-symposium
Content-Type: text/plain; charset=3D"utf-8"
Content-Transfer-Encoding: quoted-printable
MIME-Version: 1.0
X-EOPAttributedMessage: 0
X-EOPTenantAttributedMessage: 72f988bf-86f1-41af-91ab-2d7cd011db47:0
X-MS-PublicTrafficType: Email
X-MS-TrafficTypeDiagnostic: BN3PEPF00022BCB:EE_|LV2PR21MB5971:EE_
X-MS-Office365-Filtering-Correlation-Id: d8019a77-0679-499c-bc61-08df2096ce=
4b
X-MS-Exchange-AtpMessageProperties: SA|SL
X-MS-Exchange-EnableFirstContactSafetyTip: enable
X-O365-Sonar-Daas-Pilot: True
X-Forefront-Antispam-Report:
	CIP:2607:f8b0:4864:41::6;CTRY:;LANG:en;SCL:5;SRV:;IPV:NLI;SFV:SPM;H:mail-y=
x2-x06.google.com;PTR:mail-yx2-x06.google.com;CAT:SPM;SFS:(13230040)(704162=
211799003)(30052699003)(43022699015)(260918215300599003)(260918224100599003=
)(7093399015)(5063699009)(56012099006)(11063799006)(4128699003)(6123799006)=
(19002099009)(16102099003)(18002099003)(55112099003)(10067099003);DIR:INB;
X-Microsoft-Antispam:
	BCL:0;ARA:13230040|704162211799003|30052699003|43022699015|260918215300599=
003|260918224100599003|7093399015|5063699009|56012099006|11063799006|412869=
9003|6123799006|19002099009|16102099003|18002099003|55112099003|10067099003=
;
X-Microsoft-Antispam-Message-Info:
	=3D?utf-8?B?WExWcGZSbUpuK3Z4QU1EZjhHZE5uRFQ3ZnBnVDJ5RkZ5aWN2UkRCbDRGR0dJ?=
=3D
 =3D?utf-8?B?SncrVVJlbVE4dzNlU1ZNZjNuK0xSMWNEQ3dTaTduRzh5TEdxMWR2bnVuWXhT?=
=3D
 =3D?utf-8?B?REFBbVBhaGVYMVRzU0hacnh4QVlWQmZoQmszQzJtMGs2V08xMUoybDRjZitN?=
=3D
 =3D?utf-8?B?WDkwSTMwbjQ1SHh4T0FURUdQeEZESHRUSXdVRlUrL1oyL0VnQUZKQ0tuclNX?=
=3D
 =3D?utf-8?B?Z2xYcGc5cFRpaWhoZDMyTm14QTBUUFowRXZwNUgwV3hJRTFpSjFKQVgxODJH?=
=3D
 =3D?utf-8?B?ZVBvbjV6N25tYkFudVRpZktIek8yWFQyS3Jib0xOcXZKWGVZaUZGWnE3bExW?=
=3D
 =3D?utf-8?B?cXBHd1RrbHd1VUs0dkd5VE4weTA1Z2RTTFViNGFxanNFNXNkWnFTY0pCOWcr?=
=3D
 =3D?utf-8?B?dkR0QkJlbVljNndCcENKcFQ1UU9jWWtDaXJBS0dORkNJZ1dnclVaVzMrd1pN?=
=3D
 =3D?utf-8?B?YlFSQlNhbGZpTXJpRGJqa0RUTXBzdTBtMFBndnlBbzduREZ3NFBSWnhKRDNI?=
=3D
 =3D?utf-8?B?MTFFOE8xTHMrYUo4YzFPT3liVEtaNzFNMlVPRmxBcUxLaGNUQ2hSY2FCNlJr?=
=3D
 =3D?utf-8?B?dWZuaFN6WGx3MHN6SXUzSjE5VStwOHdJeDFVODh6SUVoQnMxbXpaZWgvamVF?=
=3D
 =3D?utf-8?B?Qm9oQldjZkZnVEhJNHNQTTF2WlVWVy81YXIzMUp1US9Iai9hN25lMWlCOWlP?=
=3D
 =3D?utf-8?B?amhTNlM1ZngrTmhqWk9xOTNBQnE5N09zRytQZmdtek4xclU3MVBPU1pkSEtK?=
=3D
 =3D?utf-8?B?Q3hxNEswT0IrNGJKdmhxWjMvUXZIRzA1VW9Ea004aFg4bTBONFdyL24xOWY1?=
=3D
 =3D?utf-8?B?aWRNZnY5L3ppWEQvWWNnZDZXVU9WOVRWOWxoK3R0c0dYUVVQRzkrUHZveGlM?=
=3D
 =3D?utf-8?B?ZGxTUkZvUlIrdkVqN1pwY0pXY0V1NzRtMHppVTRWei8zVHdkOFh0SnFOQjd2?=
=3D
 =3D?utf-8?B?Y04vSkhzRWlzMzdsaS9NMGwrdHRpc2tJMUJCaW9zNUluVzhKRHpSSEZHVGhQ?=
=3D
 =3D?utf-8?B?d2lvR2UvTE1tNFYyN3VrWDVscklMbkdqQWlrM3NNaUV2K2o1d1UzeTNGRTI0?=
=3D
 =3D?utf-8?B?a3VvNnlqcFVUM25pTjdxbFJESTBaSzYzdWJTRVRBRmFGNUZRWitINnRBbVpC?=
=3D
 =3D?utf-8?B?VzNSbW9UbU9SZUh2RlRFeEpteHBWRWVBanhoWGhZT2lUc054T3JLRjhBVHJ6?=
=3D
 =3D?utf-8?B?blJYVjR0c0NYandWQ09EbEhYTmxvZkYzMTRFTUt1MzdvTFBUR0JaOElhU1pB?=
=3D
 =3D?utf-8?B?MGRzSzZyREhYWXJuN3c1QUExazd6aDluMTNYVWNOK0tWOVNrdXJ1Z0Job1pX?=
=3D
 =3D?utf-8?B?eG9sNEJidzhNalJ2SnFydHMzeUVjamJRMStTUmc5NmxtVmNOZ3J6dkV2UEJw?=
=3D
 =3D?utf-8?B?Qit2d3JPUjRMV20wRVRsV1lQOCtKWWVJdzdwaVdCNzNGd2ZyWE8vY0xPQmhi?=
=3D
 =3D?utf-8?B?dGFTQ0tnVUJ6ZFZUY3I2SDYzMXJVNVJqWk9WdUIxalVaZUh0a3NOQ0JuN3gy?=
=3D
 =3D?utf-8?B?azMyZnZ0cFVaWVlSZis3TUNqZGpuYkVvOGs0c3FlVkFjUjJUT3R4bkdERWVU?=
=3D
 =3D?utf-8?B?Ri9BdWJOMXp4SmhCYWFSYlIxKzFHRDJtR2k0K0UyaFlqWW9DQUN6MVkvaktq?=
=3D
 =3D?utf-8?B?SGswaFo3N1RibzJvVmU1K25XaFU5b29NRjB1eGZWN0JrcjlYWnBUZjB2SUNK?=
=3D
 =3D?utf-8?B?UHE3WXAxSDMvdUkwcnYrM256QXVCZEJUbGlENVNwa1JXSGNGWG1vbDdTZmIx?=
=3D
 =3D?utf-8?B?cDJkblNmWVZkcEIwWkhpVjRPTEZwMzh3S2lBaUNibFlLdCtLSExTdlNjeFA1?=
=3D
 =3D?utf-8?B?TzExczlRZlhTbDdsSmZSZTkzcENaVFpXZzJtekpDS1pBMkIyUjB1bDlseXI3?=
=3D
 =3D?utf-8?B?NzBDYm4rSnFUQXh1eUtxK1dwUHplZVZtNnlYNzhtYnM5SjFoRUwyUmJXdVZI?=
=3D
 =3D?utf-8?B?bGdhbHpRczdoU2dwZ2EwdWFxdDE4Y0cwYTZmRjdqcEFXbDJnY3pSS2pPVzBS?=
=3D
 =3D?utf-8?B?b0RucStyRldvSVI1M3hWdm1ZWjFKWGYvV3podVcwTjNVSWQxeUR1b3pHVkpn?=
=3D
 =3D?utf-8?B?NDZXMUpHaWlqbTk0OURSTEtGdGxEWnFEclBtRklVYVkrVXNaS01lVFlQMkJT?=
=3D
 =3D?utf-8?B?Nk1neVRIc3I2L042WGFCZTdGcVMwQWRmbGVsRnFQN1JWR0dzdDJZcFpvd0tw?=
=3D
 =3D?utf-8?B?d2R3UnEwSkFrSW14SmhWYzZrVTNDY1ZkMnJRNUdOdlVmaHBtdG91WnE1Szg0?=
=3D
 =3D?utf-8?B?VU9JUS80em8vamJMNS8vTlpZdC9ZQi9IYnZNT1dtQTVubmNuQzYzSkM4bWRP?=
=3D
 =3D?utf-8?B?NG9DZlYrSDhqeDZYeWFuQlBuN1pSem5oL3NCVG1aRlJaTC9hSlNOcHVuMWR6?=
=3D
 =3D?utf-8?B?alJNQ1JGV1JIV3llcUIzV3hQbU1rbXI3RUVWUjV0RGNBNktpdkUydjVjVU90?=
=3D
 =3D?utf-8?B?d3dmdG5CbysxM1BncFl5UXgxRjI1Z1E3YnlEWXFTMHFnTmRCeGkzd3RTc09F?=
=3D
 =3D?utf-8?B?UzRCNEtySXZHU2VZVTVLdHRFbktDbXhIUjVZcURKM1E1ZVhaU09KTTZzR2FE?=
=3D
 =3D?utf-8?B?ZldQV0taYlZMQWd1WUxTT0U4dnpVbnllRGZ0VVJweS9VSzhVYm41NXFaSW0y?=
=3D
 =3D?utf-8?B?N1U0NWxGWnZlb3JKK1B6Z1FXSmlJRlFrMWFOWGJEcGZMcjQwWDM2NVZkVElP?=
=3D
 =3D?utf-8?B?dXE3SitUam1ISVlVai9rU0hDbk44STZLNUcvamxUNlZvWnhvbFpma0FUUTRM?=
=3D
 =3D?utf-8?B?Ync2TXVaenZpS1NZN2M4VUlZamN3UVFhTVdGbzA1cUoyWXJGM0pTWjRMM1JN?=
=3D
 =3D?utf-8?B?ZmU2b0J4bWpQcU5jU2RhUjI0ZGFVclIvZm9PbDdNckZ5ZWNRaTFTUlJtNHNM?=
=3D
 =3D?utf-8?B?d2p4b1Z4R3luWVcvdkRsUm5VaXNkc0lhanI2aHlUUGFFcURZd0JWb0JCSm9H?=
=3D
 =3D?utf-8?B?K1NaTlAzeEJTLzVlOEY1dU9icndVWmpWMjBDazVGSGNxY21lZXp4L0R2SUxj?=
=3D
 =3D?utf-8?B?VlNkV0ZHcEU4R2V2R0MzTEpRSjcxYWp3S25JeU5TN2VtYnZrVVRHSmNIaS9K?=
=3D
 =3D?utf-8?B?RlE2RXVWMWxoeG5jVEJuS0RDQ2dxNjNOVVV1WEdvWkdOK2lTbEpnd3o0ZmR3?=
=3D
 =3D?utf-8?B?NEJrNlhuaWRCN01GOXBqdzhTR1RCUTRDbmpBNzZ4ZkhaMXF3dmlEdlp4NTlU?=
=3D
 =3D?utf-8?B?bVY4N3lZM1dzdG5aWFdqM0ppVDdRcGkrNG5JeUF0RnRqSDBETm9wNkRTNlVL?=
=3D
 =3D?utf-8?B?WUN0ZFhmaXNDZldiUjEvQ0hmNjJYZ2hhUnRLTk1vNXVQamhxMDlvYXJZb2Js?=
=3D
 =3D?utf-8?B?Z2d4MS95NDZUMmhxMjhXS3lzREdBaFM2NE1sakVrUDJzYVdzc2ZKaTl2VFNB?=
=3D
 =3D?utf-8?B?VlpXQzhZWThPRDlldnVPS0cwUnR4K3Q1V1paaVRUaWZwQlhyK2RSb2NMdlo0?=
=3D
 =3D?utf-8?B?Vi9rTGNCN2s5UkZndFFPenZwQUF5Zk96TlE2YlRmdlBDZjRZbzl3a1hXYllR?=
=3D
 =3D?utf-8?B?WmFjUEJCeWorcE5oSW9JaWZOYzREdzlISUNyMy9DcDRQTDhORTdJV1ZLTkZK?=
=3D
 =3D?utf-8?B?alhKQkcyNGN3Umo0aWxMTmthZk1EVlZiay9aZFgwMDN3YTlFb01KczhndFV2?=
=3D
 =3D?utf-8?B?MUU0b0hGeXFreGtjemoyYzk0enZPbm1xL1VWclJ6YlUzWUxxZ2ZvNkU1RXdT?=
=3D
 =3D?utf-8?B?VkFpU0w0QTJ6ZWh3Y1ZxUEtPeTFPdjIxVFEvbmJSbnFyRWhtRmdHNkR0Nmhp?=
=3D
 =3D?utf-8?B?STl1UktxUittMlplL1dnZHZXYzBXMlcvRkp2Mmo2NHowT0ZicGlCa3I2SjVh?=
=3D
 =3D?utf-8?B?ME9EUkI1c3FhQXB0WHhPWktJZm1odEczWGI3WXVnMW9RYXBLUEg2eEx6eEMy?=
=3D
 =3D?utf-8?B?ZFRYaHFkK2kvU1hmSTA4K1lGREc5ejNMZE5RNXJkaTZwbkpsRjVDcGRidWlw?=
=3D
 =3D?utf-8?B?NlpnamEzWVA5TWJLT1BCZFlRSzJVR2NFVWxPNHRWQ2lSYkZxZXZlY2tmbDVY?=
=3D
 =3D?utf-8?B?N29VSmMwdzcxTXhNbFYvSE5QNWVFazh1ZVBVVVgyakI3cElDeDlOWXJ2MTI4?=
=3D
 =3D?utf-8?B?ek1rT0ovT25GR1hWSWN5cUowQlMrWGlvTDdlUXEzdXZUMVlVa3pLamFZWnNE?=
=3D
 =3D?utf-8?B?cnpWb0wvOTRXRktCZGplQWllRnYrak14VSs3MXVHUTNtcnEvRWJ6cHB3d3o1?=
=3D
 =3D?utf-8?B?MVVZWU90RmttZHdoSkRCbjFpQ05VTHpvZGdBbXZCU0V5d2pYMkk4Z1cvc2wy?=
=3D
 =3D?utf-8?Q?jSsNWxhINw=3D3D?=3D
X-Exchange-RoutingPolicyChecked:
	mPun7tz21ZkR9l+cVsoyu7o+eJblFya7fSMJI60X0YNMdeqnbm4uzPZaljRI5XzYZiBA6l9mKu=
2icBXjEAceqY1+lnRZXvXHiI2EzEcRfiB3ZCgKgpr10dhpTDHy4Qp0SBfbJzfVlX61tLEvA0tSi=
ZV5A+lkUWbAH6CPQRuDJxet2avYsQDLChOiavxe+2rqXbWwjJCZwxNrrzrL7X5LVbXXTg8TRCri=
STZu715tuxsPtGx4PxKktz9mYP4PIhkgjb/UFM4qO2cqMiU3N+DWGMYuXlXTTxRnV+ZFk52otED=
dOLnXrR6xjt1h8jnky/DyobarfJgSlkjiRg0ho8R/pQ=3D=3D
X-OriginatorOrg: microsoft.onmicrosoft.com
X-MS-Exchange-CrossTenant-OriginalArrivalTime: 02 Oct 2026 15:06:58.8118
 (UTC)
X-MS-Exchange-CrossTenant-Network-Message-Id: d8019a77-0679-499c-bc61-08df2=
096ce4b
X-MS-Exchange-CrossTenant-Id: 72f988bf-86f1-41af-91ab-2d7cd011db47
X-MS-Exchange-CrossTenant-AuthSource:
	BN3PEPF00022BCB.namprd03.prod.outlook.com
X-MS-Exchange-CrossTenant-AuthAs: Anonymous
X-MS-Exchange-CrossTenant-FromEntityHeader: Internet
X-MS-Exchange-Transport-CrossTenantHeadersStamped: LV2PR21MB5971
