/*
 * Copyright (C) 2003 Carnegie Mellon University and Rutgers University
 *
 * Permission is hereby granted to distribute this software for
 * non-commercial research purposes, provided that this copyright
 * notice is included with any such distribution.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
 * EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE
 * SOFTWARE IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU
 * ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
 *
 * $Id: exceptions.cc,v 1.1 2003/11/07 03:04:33 john Exp $
 */
#include "exceptions.h"


/* ====================================================================== */
/* Exception */

/* Constructs an exception. */
Exception::Exception(const std::string& msg)
  : msg_(msg) {}


/* Output operator for runtime exceptions. */
std::ostream& operator<<(std::ostream& os, const Exception& e) {
  return os << e.msg_;
}
