[![Build Status](https://travis-ci.org/akretion/odoo-shopinvader.svg?branch=10.0)](https://travis-ci.org/akretion/odoo-shopinvader)
[![codecov](https://codecov.io/gh/akretion/odoo-shopinvader/branch/10.0/graph/badge.svg)](https://codecov.io/gh/akretion/odoo-shopinvader/branch/10.0)
[![Code Climate](https://codeclimate.com/github/akretion/odoo-shopinvader/badges/gpa.svg)](https://codeclimate.com/github/akretion/odoo-shopinvader)


ShopInvader
=================

Web alternative solution based on locomotivecms







Migration
===========

A list of pending module waiting (and maybe started module) can be found here
https://github.com/akretion/shopinvader-odoo/tree/10.0-to-migrate

If you want to migrate it just run the following command

```
git checkout -b 10.0-mig-$MODULE origin/10.0

git format-patch --keep-subject --stdout origin/10.0..origin/10.0-to-migrate -- $MODULE | git am -3 --keep

```


Documentation
===============

A work in progress documentation is available here : https://akretion.github.io/shopinvader-documentation
